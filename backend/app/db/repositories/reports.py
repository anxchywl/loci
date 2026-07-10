import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Comment, Report, Story


async def create_for_story(
    db: AsyncSession, *, story_id: uuid.UUID, reporter_id: int, reason: str | None
) -> None:
    stmt = (
        postgres_insert(Report)
        .values(story_id=story_id, reporter_id=reporter_id, reason=reason)
        # the unique index is partial, so the predicate must be repeated here
        .on_conflict_do_nothing(
            index_elements=[Report.reporter_id, Report.story_id],
            index_where=Report.story_id.is_not(None),
        )
    )
    await db.execute(stmt)
    await db.flush()


async def create_for_comment(
    db: AsyncSession, *, comment_id: uuid.UUID, reporter_id: int, reason: str | None
) -> None:
    stmt = (
        postgres_insert(Report)
        .values(comment_id=comment_id, reporter_id=reporter_id, reason=reason)
        .on_conflict_do_nothing(
            index_elements=[Report.reporter_id, Report.comment_id],
            index_where=Report.comment_id.is_not(None),
        )
    )
    await db.execute(stmt)
    await db.flush()


async def count_distinct_story_reporters(db: AsyncSession, story_id: uuid.UUID) -> int:
    # a story's own author reporting it must not count toward auto-hide
    author = select(Story.author_id).where(Story.id == story_id).scalar_subquery()
    stmt = (
        select(func.count(func.distinct(Report.reporter_id)))
        .where(
            and_(
                Report.story_id == story_id,
                Report.resolved_at.is_(None),
                Report.reporter_id.is_not(None),
                Report.reporter_id != author,
            )
        )
    )
    return (await db.execute(stmt)).scalar_one()


async def count_distinct_comment_reporters(db: AsyncSession, comment_id: uuid.UUID) -> int:
    author = select(Comment.author_id).where(Comment.id == comment_id).scalar_subquery()
    stmt = (
        select(func.count(func.distinct(Report.reporter_id)))
        .where(
            and_(
                Report.comment_id == comment_id,
                Report.resolved_at.is_(None),
                Report.reporter_id.is_not(None),
                Report.reporter_id != author,
            )
        )
    )
    return (await db.execute(stmt)).scalar_one()
