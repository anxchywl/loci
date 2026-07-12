import time

import pytest
from fakeredis.aioredis import FakeRedis

from app.core.security.telegram import (
    TelegramInitDataError,
    reject_replayed_init_data,
    validate_telegram_init_data,
)
from tests.factories import TEST_BOT_TOKEN, build_init_data

MAX_AGE = 300


def validate(init_data: str, bot_token: str = TEST_BOT_TOKEN):
    return validate_telegram_init_data(init_data, bot_token, MAX_AGE)


def test_valid_init_data_returns_user():
    user = validate(build_init_data(telegram_id=42, username="aru", language_code="kk"))
    assert user.telegram_id == 42
    assert user.username == "aru"
    assert user.language_code == "kk"


def test_tampered_payload_rejected():
    init_data = build_init_data(username="aru")
    tampered = init_data.replace("aru", "eve")
    with pytest.raises(TelegramInitDataError, match="hash is invalid"):
        validate(tampered)


def test_wrong_bot_token_rejected():
    init_data = build_init_data(bot_token="999999:OTHER-TOKEN")
    with pytest.raises(TelegramInitDataError, match="hash is invalid"):
        validate(init_data)


def test_missing_hash_rejected():
    with pytest.raises(TelegramInitDataError, match="hash is missing"):
        validate("auth_date=123&user=%7B%7D")


def test_stale_auth_date_rejected():
    init_data = build_init_data(auth_date=int(time.time()) - MAX_AGE - 60)
    with pytest.raises(TelegramInitDataError, match="expired"):
        validate(init_data)


def test_future_auth_date_rejected():
    init_data = build_init_data(auth_date=int(time.time()) + 600)
    with pytest.raises(TelegramInitDataError, match="future"):
        validate(init_data)


def test_missing_user_payload_rejected():
    init_data = build_init_data()
    without_user = "&".join(
        part for part in init_data.split("&") if not part.startswith("user=")
    )
    with pytest.raises(TelegramInitDataError):
        validate(without_user)


def test_empty_bot_token_rejected():
    with pytest.raises(TelegramInitDataError, match="not configured"):
        validate(build_init_data(), bot_token="")


def test_malformed_timestamp_is_rejected_without_server_error():
    init_data = build_init_data(extra={"auth_date": "999999999999999999999999"})
    with pytest.raises(TelegramInitDataError, match="auth_date is invalid"):
        validate(init_data)


def test_duplicate_fields_are_rejected():
    init_data = build_init_data()
    with pytest.raises(TelegramInitDataError, match="duplicate fields"):
        validate(f"{init_data}&auth_date=1")


async def test_replay_guard_rejects_second_use():
    redis = FakeRedis(decode_responses=True)
    init_data = build_init_data()
    await reject_replayed_init_data(redis, init_data, MAX_AGE)
    with pytest.raises(TelegramInitDataError, match="already used"):
        await reject_replayed_init_data(redis, init_data, MAX_AGE)


async def test_replay_guard_allows_distinct_payloads():
    redis = FakeRedis(decode_responses=True)
    await reject_replayed_init_data(redis, build_init_data(telegram_id=1), MAX_AGE)
    await reject_replayed_init_data(redis, build_init_data(telegram_id=2), MAX_AGE)
