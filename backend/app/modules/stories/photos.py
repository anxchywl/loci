import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.repositories import photos as photos_repo
from app.db.repositories import stories as stories_repo
from app.integrations import storage
from app.modules.stories.schemas import PhotoUploadResponse
from app.modules.stories.service import StoryNotFound

_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
}


async def create_upload_url(
    db: AsyncSession,
    story_id: uuid.UUID,
    author_id: int,
    content_type: str,
    settings: Settings,
) -> PhotoUploadResponse:
    story = await stories_repo.get_owned(db, story_id, author_id)
    if story is None:
        raise StoryNotFound()

    if await photos_repo.count_for_story(db, story_id) >= settings.max_photos_per_story:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"a story can have at most {settings.max_photos_per_story} photos",
        )

    photo_id = uuid.uuid4()
    extension = _EXTENSIONS[content_type]
    object_key = f"stories/{story_id}/{photo_id}/original.{extension}"

    position = await photos_repo.count_for_story(db, story_id)
    photo = await photos_repo.create(
        db,
        photo_id=photo_id,
        story_id=story_id,
        object_key=object_key,
        content_type=content_type,
        position=position,
    )
    await db.commit()

    ttl = settings.s3_presigned_url_expires_seconds
    upload_url = storage.presigned_put_url(object_key, ttl)
    return PhotoUploadResponse(photo_id=photo.id, upload_url=upload_url, expires_in=ttl)


async def complete_upload(
    db: AsyncSession,
    story_id: uuid.UUID,
    photo_id: uuid.UUID,
    author_id: int,
    settings: Settings,
) -> None:
    # optimization is queued only after the client confirms the bytes are in the bucket
    story = await stories_repo.get_owned(db, story_id, author_id)
    if story is None:
        raise StoryNotFound()

    photo = await photos_repo.get(db, photo_id)
    if photo is None or photo.story_id != story_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    object_size = storage.get_object_size(photo.object_key)
    if object_size is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Photo upload not found")

    max_upload_bytes = settings.max_upload_size_mb * 1024 * 1024
    if object_size > max_upload_bytes:
        storage.delete_object(photo.object_key)
        await photos_repo.mark_failed(db, photo.id)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Photo must not exceed {settings.max_upload_size_mb} MB",
        )

    from app.workers.tasks import optimize_photo

    optimize_photo.delay(str(photo.id))
