import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qsl

from redis.asyncio import Redis


class TelegramInitDataError(Exception):
    pass


_MAX_INIT_DATA_LENGTH = 8192
_MAX_INIT_DATA_FIELDS = 64
_MAX_TELEGRAM_ID = 2**52 - 1


@dataclass(frozen=True)
class TelegramUserData:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    photo_url: str | None
    language_code: str | None


def validate_telegram_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: int,
) -> TelegramUserData:
    if not bot_token:
        raise TelegramInitDataError("Telegram bot token is not configured")

    if not init_data or len(init_data) > _MAX_INIT_DATA_LENGTH:
        raise TelegramInitDataError("Telegram init data is invalid")

    try:
        pairs = parse_qsl(
            init_data,
            keep_blank_values=True,
            strict_parsing=True,
            max_num_fields=_MAX_INIT_DATA_FIELDS,
        )
    except ValueError as exc:
        raise TelegramInitDataError("Telegram init data is invalid") from exc

    if len({key for key, _ in pairs}) != len(pairs):
        raise TelegramInitDataError("Telegram init data contains duplicate fields")

    parsed = dict(pairs)
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise TelegramInitDataError("Telegram init data hash is missing")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramInitDataError("Telegram init data hash is invalid")

    auth_date_raw = parsed.get("auth_date")
    if not auth_date_raw:
        raise TelegramInitDataError("Telegram auth_date is missing")

    try:
        auth_date = datetime.fromtimestamp(int(auth_date_raw), tz=UTC)
    except (ValueError, OverflowError, OSError) as exc:
        raise TelegramInitDataError("Telegram auth_date is invalid") from exc

    age_seconds = (datetime.now(UTC) - auth_date).total_seconds()
    if age_seconds > max_age_seconds:
        raise TelegramInitDataError("Telegram init data is expired")
    # reject timestamps from the future (small skew allowed) so a forged auth_date
    # cannot produce a never-expiring payload
    if age_seconds < -60:
        raise TelegramInitDataError("Telegram auth_date is in the future")

    user_raw = parsed.get("user")
    if not user_raw:
        raise TelegramInitDataError("Telegram user payload is missing")

    try:
        user_payload = json.loads(user_raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise TelegramInitDataError("Telegram user payload is invalid") from exc

    if not isinstance(user_payload, dict):
        raise TelegramInitDataError("Telegram user payload is invalid")

    telegram_id = user_payload.get("id")
    if (
        not isinstance(telegram_id, int)
        or isinstance(telegram_id, bool)
        or not 0 < telegram_id <= _MAX_TELEGRAM_ID
    ):
        raise TelegramInitDataError("Telegram user id is invalid")

    return TelegramUserData(
        telegram_id=telegram_id,
        username=_optional_string(user_payload.get("username")),
        first_name=_optional_string(user_payload.get("first_name")),
        last_name=_optional_string(user_payload.get("last_name")),
        photo_url=_optional_string(user_payload.get("photo_url")),
        language_code=_optional_string(user_payload.get("language_code")),
    )


async def reject_replayed_init_data(
    redis: Redis,
    init_data: str,
    max_age_seconds: int,
) -> None:
    # key the guard on the whole payload; after the ttl the staleness check rejects it anyway
    key = "auth:initdata:" + hashlib.sha256(init_data.encode("utf-8")).hexdigest()
    stored = await redis.set(key, "1", nx=True, ex=max_age_seconds + 60)
    if not stored:
        raise TelegramInitDataError("Telegram init data was already used")


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None
