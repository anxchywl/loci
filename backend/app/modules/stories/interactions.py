import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.repositories import bookmarks as bookmarks_repo
from app.db.repositories import comments as comments_repo
from app.db.repositories import reactions as reactions_repo
from app.db.repositories import reports as reports_repo
from app.db.repositories import stories as stories_repo
from app.modules.stories.service import StoryNotFound, _assert_readable


async def react(db: AsyncSession, story_id: uuid.UUID, user_id: int) -> None:
    await _assert_readable(db, story_id, user_id)
    await reactions_repo.add(db, story_id, user_id)
    await db.commit()


async def unreact(db: AsyncSession, story_id: uuid.UUID, user_id: int) -> None:
    await _assert_readable(db, story_id, user_id)
    await reactions_repo.remove(db, story_id, user_id)
    await db.commit()


async def bookmark(db: AsyncSession, story_id: uuid.UUID, user_id: int) -> None:
    await _assert_readable(db, story_id, user_id)
    await bookmarks_repo.add(db, story_id, user_id)
    await db.commit()


async def unbookmark(db: AsyncSession, story_id: uuid.UUID, user_id: int) -> None:
    await _assert_readable(db, story_id, user_id)
    await bookmarks_repo.remove(db, story_id, user_id)
    await db.commit()


async def report_story(
    db: AsyncSession,
    story_id: uuid.UUID,
    reporter_id: int,
    reason: str | None,
    settings: Settings,
) -> None:
    await _assert_readable(db, story_id, reporter_id)
    await reports_repo.create_for_story(db, story_id=story_id, reporter_id=reporter_id, reason=reason)

    reporters = await reports_repo.count_distinct_story_reporters(db, story_id)
    if reporters >= settings.report_auto_hide_threshold:
        await stories_repo.set_hidden(db, story_id, True)
    await db.commit()


async def report_comment(
    db: AsyncSession,
    comment_id: uuid.UUID,
    reporter_id: int,
    reason: str | None,
    settings: Settings,
) -> None:
    comment = await comments_repo.get(db, comment_id)
    if comment is None or comment.is_hidden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    await _assert_readable(db, comment.story_id, reporter_id)

    await reports_repo.create_for_comment(
        db, comment_id=comment_id, reporter_id=reporter_id, reason=reason
    )
    reporters = await reports_repo.count_distinct_comment_reporters(db, comment_id)
    if reporters >= settings.report_auto_hide_threshold:
        await comments_repo.set_hidden(db, comment_id, True)
    await db.commit()


__all__ = [
    "StoryNotFound",
    "bookmark",
    "react",
    "report_comment",
    "report_story",
    "unbookmark",
    "unreact",
]
