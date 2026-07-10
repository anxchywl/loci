from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.telegram import TelegramUserData
from app.db.models import User


async def upsert_from_telegram(db: AsyncSession, data: TelegramUserData) -> User:
    stmt = (
        postgres_insert(User)
        .values(
            telegram_id=data.telegram_id,
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            language_code=data.language_code,
            photo_url=data.photo_url,
        )
        .on_conflict_do_update(
            index_elements=[User.__table__.c.telegram_id],
            set_={
                "username": data.username,
                "first_name": data.first_name,
                "last_name": data.last_name,
                "language_code": data.language_code,
                "photo_url": data.photo_url,
                "updated_at": func.now(),
            },
        )
        .returning(User.id)
    )
    user_id = (await db.execute(stmt)).scalar_one()
    user = await db.get(User, user_id)
    assert user is not None
    return user


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)
