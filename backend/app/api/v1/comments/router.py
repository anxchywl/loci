import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session, get_redis
from app.core.config import Settings, get_settings
from app.core.security.rate_limit import check_rate_limit
from app.db.models import User
from app.modules.stories import interactions, service
from app.modules.stories.schemas import ReportCreateRequest

router = APIRouter(prefix="/comments", tags=["comments"])


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    await check_rate_limit(
        redis, "rl:comment-delete", str(user.id), 60, settings.comment_deletes_per_minute
    )
    await service.delete_comment(db, comment_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{comment_id}/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_comment(
    comment_id: uuid.UUID,
    payload: ReportCreateRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    await check_rate_limit(redis, "rl:report", str(user.id), 86400, settings.reports_per_day)
    await interactions.report_comment(db, comment_id, user.id, payload.reason, settings)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
