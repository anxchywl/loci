import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import Settings


class TokenError(Exception):
    pass


def create_access_token(
    user_id: int,
    settings: Settings,
    session_id: uuid.UUID | None = None,
) -> tuple[str, datetime]:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    claims: dict[str, object] = {
        "sub": str(user_id),
        "type": "access",
        "exp": expires_at,
        "iat": datetime.now(UTC),
        "iss": "loci-api",
        "aud": "loci-client",
    }
    if session_id is not None:
        claims["sid"] = str(session_id)
    token = jwt.encode(
        claims,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_at


def decode_access_token(token: str, settings: Settings) -> tuple[int, uuid.UUID | None]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience="loci-client",
            issuer="loci-api",
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Invalid access token") from exc

    if payload.get("type") != "access":
        raise TokenError("Invalid token type")

    subject = payload.get("sub")
    if not subject:
        raise TokenError("Missing token subject")

    try:
        user_id = int(subject)
    except (ValueError, TypeError) as exc:
        raise TokenError("Invalid token subject") from exc

    session_id_raw = payload.get("sid")
    if session_id_raw is None:
        return user_id, None
    if not isinstance(session_id_raw, str):
        raise TokenError("Invalid token session")
    try:
        session_id = uuid.UUID(session_id_raw)
    except ValueError as exc:
        raise TokenError("Invalid token session") from exc
    return user_id, session_id
