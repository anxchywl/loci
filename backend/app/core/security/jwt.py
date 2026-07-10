from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import Settings


class TokenError(Exception):
    pass


def create_access_token(user_id: int, settings: Settings) -> tuple[str, datetime]:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    token = jwt.encode(
        {
            "sub": str(user_id),
            "type": "access",
            "exp": expires_at,
            "iat": datetime.now(UTC),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_at


def decode_access_token(token: str, settings: Settings) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Invalid access token") from exc

    if payload.get("type") != "access":
        raise TokenError("Invalid token type")

    subject = payload.get("sub")
    if not subject:
        raise TokenError("Missing token subject")

    try:
        return int(subject)
    except ValueError as exc:
        raise TokenError("Invalid token subject") from exc
