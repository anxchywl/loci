from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Category


async def list_all(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.position))
    return list(result.scalars().all())


async def exists(db: AsyncSession, category_id: int) -> bool:
    result = await db.execute(select(Category.id).where(Category.id == category_id))
    return result.scalar_one_or_none() is not None
