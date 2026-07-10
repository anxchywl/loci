import uuid

from sqlalchemy import delete as sql_delete
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Bookmark


async def add(db: AsyncSession, story_id: uuid.UUID, user_id: int) -> None:
    stmt = (
        postgres_insert(Bookmark)
        .values(story_id=story_id, user_id=user_id)
        .on_conflict_do_nothing(index_elements=[Bookmark.user_id, Bookmark.story_id])
    )
    await db.execute(stmt)
    await db.flush()


async def remove(db: AsyncSession, story_id: uuid.UUID, user_id: int) -> None:
    await db.execute(
        sql_delete(Bookmark).where(Bookmark.story_id == story_id, Bookmark.user_id == user_id)
    )
    await db.flush()
