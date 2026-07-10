from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.db.repositories import categories as categories_repo
from app.modules.stories.schemas import CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[CategoryResponse]:
    categories = await categories_repo.list_all(db)
    return [CategoryResponse.model_validate(category) for category in categories]
