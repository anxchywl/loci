import uuid
from datetime import date

from geoalchemy2 import Geography
from sqlalchemy import Select, and_, cast, false, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Bookmark, Comment, Reaction, Story, StoryVisibility, User
from app.db.models.story import LocationPrecision

# location_exact is never selected on any read path; when precision is exact the
# public column already holds the same point
STORY_READ_COLUMNS = (
    Story.id,
    Story.author_id,
    Story.category_id,
    Story.title,
    Story.body,
    Story.happened_on,
    Story.is_anonymous,
    Story.visibility,
    Story.location_precision,
    Story.created_at,
    func.ST_Y(Story.location_public).label("lat"),
    func.ST_X(Story.location_public).label("lon"),
    User.username.label("author_username"),
    User.first_name.label("author_first_name"),
    User.photo_url.label("author_photo_url"),
)


def _counts(viewer_id: int | None):
    # correlate(Story) is required: without it these subqueries auto-correlate against
    # a joined reactions/bookmarks table and lose their own FROM clause
    reactions = (
        select(func.count())
        .select_from(Reaction)
        .where(Reaction.story_id == Story.id)
        .correlate(Story)
        .scalar_subquery()
        .label("reaction_count")
    )
    comments = (
        select(func.count())
        .select_from(Comment)
        .where(and_(Comment.story_id == Story.id, Comment.is_hidden.is_(False)))
        .correlate(Story)
        .scalar_subquery()
        .label("comment_count")
    )
    if viewer_id is None:
        return (
            reactions,
            comments,
            false().label("viewer_reacted"),
            false().label("viewer_bookmarked"),
        )

    reacted = (
        select(func.count() > 0)
        .select_from(Reaction)
        .where(and_(Reaction.story_id == Story.id, Reaction.user_id == viewer_id))
        .correlate(Story)
        .scalar_subquery()
        .label("viewer_reacted")
    )
    bookmarked = (
        select(func.count() > 0)
        .select_from(Bookmark)
        .where(and_(Bookmark.story_id == Story.id, Bookmark.user_id == viewer_id))
        .correlate(Story)
        .scalar_subquery()
        .label("viewer_bookmarked")
    )
    return reactions, comments, reacted, bookmarked


def _visible_to(viewer_id: int | None):
    # private stories are only ever readable by their author; hidden ones by nobody
    public = and_(
        Story.visibility == StoryVisibility.public,
        Story.is_hidden.is_(False),
    )
    if viewer_id is None:
        return public
    return or_(public, and_(Story.author_id == viewer_id, Story.is_hidden.is_(False)))


def _base_select(viewer_id: int | None) -> Select:
    reactions, comments, reacted, bookmarked = _counts(viewer_id)
    return (
        select(*STORY_READ_COLUMNS, reactions, comments, reacted, bookmarked)
        .outerjoin(User, User.id == Story.author_id)
        .where(_visible_to(viewer_id))
    )


async def create(
    db: AsyncSession,
    *,
    author_id: int,
    category_id: int,
    title: str,
    body: str,
    happened_on: date | None,
    is_anonymous: bool,
    visibility: StoryVisibility,
    precision: LocationPrecision,
    exact_lat: float,
    exact_lon: float,
) -> uuid.UUID:
    story = Story(
        author_id=author_id,
        category_id=category_id,
        title=title,
        body=body,
        happened_on=happened_on,
        is_anonymous=is_anonymous,
        visibility=visibility,
        location_precision=precision,
        location_exact=func.ST_SetSRID(func.ST_MakePoint(exact_lon, exact_lat), 4326),
        location_public=func.ST_SetSRID(func.ST_MakePoint(exact_lon, exact_lat), 4326),
    )
    db.add(story)
    await db.flush()
    return story.id


async def set_public_point(db: AsyncSession, story_id: uuid.UUID, lat: float, lon: float) -> None:
    story = await db.get(Story, story_id)
    assert story is not None
    story.location_public = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    await db.flush()


async def get_owned(db: AsyncSession, story_id: uuid.UUID, author_id: int) -> Story | None:
    story = await db.get(Story, story_id)
    if story is None or story.author_id != author_id:
        return None
    return story


async def get_for_viewer(db: AsyncSession, story_id: uuid.UUID, viewer_id: int | None):
    stmt = _base_select(viewer_id).where(Story.id == story_id)
    return (await db.execute(stmt)).mappings().one_or_none()


async def list_nearby(
    db: AsyncSession,
    *,
    viewer_id: int | None,
    lat: float,
    lon: float,
    radius_meters: int,
    category_id: int | None,
    limit: int,
):
    point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    # geography cast makes the radius metric and wraps the antimeridian correctly
    story_geog = cast(Story.location_public, Geography)
    point_geog = cast(point, Geography)
    stmt = _base_select(viewer_id).where(func.ST_DWithin(story_geog, point_geog, radius_meters))
    if category_id is not None:
        stmt = stmt.where(Story.category_id == category_id)
    stmt = stmt.order_by(func.ST_Distance(story_geog, point_geog)).limit(limit)
    return (await db.execute(stmt)).mappings().all()


async def list_in_bbox(
    db: AsyncSession,
    *,
    viewer_id: int | None,
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    category_id: int | None,
    limit: int,
):
    envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    stmt = _base_select(viewer_id).where(func.ST_Intersects(Story.location_public, envelope))
    if category_id is not None:
        stmt = stmt.where(Story.category_id == category_id)
    stmt = stmt.order_by(Story.created_at.desc()).limit(limit)
    return (await db.execute(stmt)).mappings().all()


async def list_trending(db: AsyncSession, *, viewer_id: int | None, limit: int):
    reactions, comments, reacted, bookmarked = _counts(viewer_id)
    stmt = (
        select(*STORY_READ_COLUMNS, reactions, comments, reacted, bookmarked)
        .outerjoin(User, User.id == Story.author_id)
        .where(_visible_to(viewer_id))
        .order_by((reactions + comments).desc(), Story.created_at.desc())
        .limit(limit)
    )
    return (await db.execute(stmt)).mappings().all()


async def search(db: AsyncSession, *, viewer_id: int | None, query: str, limit: int):
    pattern = f"%{query}%"
    stmt = (
        _base_select(viewer_id)
        .where(or_(Story.title.ilike(pattern), Story.body.ilike(pattern)))
        .order_by(Story.created_at.desc())
        .limit(limit)
    )
    return (await db.execute(stmt)).mappings().all()


async def list_by_author(
    db: AsyncSession,
    *,
    author_id: int,
    viewer_id: int | None,
    limit: int,
    include_anonymous: bool = False,
):
    stmt = _base_select(viewer_id).where(Story.author_id == author_id)
    # a user's anonymous stories are listed only on their own profile
    if not include_anonymous:
        stmt = stmt.where(Story.is_anonymous.is_(False))
    stmt = stmt.order_by(Story.created_at.desc()).limit(limit)
    return (await db.execute(stmt)).mappings().all()


async def list_bookmarked(db: AsyncSession, *, viewer_id: int, limit: int):
    stmt = (
        _base_select(viewer_id)
        .join(Bookmark, Bookmark.story_id == Story.id)
        .where(Bookmark.user_id == viewer_id)
        .order_by(Bookmark.created_at.desc())
        .limit(limit)
    )
    return (await db.execute(stmt)).mappings().all()


async def delete(db: AsyncSession, story: Story) -> None:
    await db.delete(story)
    await db.flush()


async def count_by_author_since(db: AsyncSession, author_id: int, since) -> int:
    stmt = (
        select(func.count())
        .select_from(Story)
        .where(and_(Story.author_id == author_id, Story.created_at >= since))
    )
    return (await db.execute(stmt)).scalar_one()


async def set_hidden(db: AsyncSession, story_id: uuid.UUID, hidden: bool) -> None:
    story = await db.get(Story, story_id)
    if story is not None:
        story.is_hidden = hidden
        await db.flush()
