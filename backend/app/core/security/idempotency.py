import hashlib
import json
import logging
import secrets
from dataclasses import dataclass

from fastapi import HTTPException, status
from redis.asyncio import Redis
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IdempotencyReservation:
    key: str
    owner: str
    request_hash: str


def request_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def begin(
    redis: Redis,
    *,
    scope: str,
    user_id: int,
    idempotency_key: str | None,
    request_hash_value: str,
    ttl_seconds: int,
) -> tuple[IdempotencyReservation | None, str | None]:
    if not idempotency_key:
        return None, None
    if len(idempotency_key) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Idempotency-Key is too long",
        )

    key = f"idempotency:{scope}:{user_id}:{idempotency_key}"
    try:
        cached = await redis.get(key)
        if cached:
            record = json.loads(cached)
            if record.get("request_hash") != request_hash_value:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency-Key was already used for a different request",
                )
            if record.get("state") != "complete":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The request with this Idempotency-Key is still in progress",
                )
            return None, record["response"]

        owner = secrets.token_urlsafe(24)
        reservation = json.dumps(
            {"state": "pending", "owner": owner, "request_hash": request_hash_value}
        )
        stored = await redis.set(key, reservation, nx=True, ex=ttl_seconds)
        if not stored:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The request with this Idempotency-Key is still in progress",
            )
        return IdempotencyReservation(key, owner, request_hash_value), None
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="idempotency protection is temporarily unavailable",
        ) from exc


async def complete(
    redis: Redis,
    reservation: IdempotencyReservation,
    response: str,
    ttl_seconds: int,
) -> None:
    value = json.dumps(
        {
            "state": "complete",
            "owner": reservation.owner,
            "request_hash": reservation.request_hash,
            "response": response,
        }
    )
    try:
        await redis.set(reservation.key, value, ex=ttl_seconds)
    except RedisError:
        logger.warning("idempotency result could not be stored")


async def abandon(redis: Redis, reservation: IdempotencyReservation) -> None:
    try:
        current = await redis.get(reservation.key)
        if current:
            record = json.loads(current)
            if record.get("owner") == reservation.owner:
                await redis.delete(reservation.key)
    except (RedisError, json.JSONDecodeError):
        return
