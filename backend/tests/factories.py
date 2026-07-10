import hashlib
import hmac
import itertools
import json
import time
from urllib.parse import urlencode

_nonce = itertools.count()

TEST_BOT_TOKEN = "123456:TEST-TOKEN"


def build_init_data(
    *,
    bot_token: str = TEST_BOT_TOKEN,
    telegram_id: int = 100500,
    username: str | None = "loci_mapper",
    first_name: str = "Aru",
    language_code: str = "kk",
    auth_date: int | None = None,
    extra: dict[str, str] | None = None,
) -> str:
    user: dict[str, object] = {"id": telegram_id, "first_name": first_name}
    if username is not None:
        user["username"] = username
    if language_code is not None:
        user["language_code"] = language_code

    fields = {
        "auth_date": str(auth_date if auth_date is not None else int(time.time())),
        # unique per call so the replay guard doesn't reject repeated logins in a test
        "query_id": f"AAtest{next(_nonce)}",
        "user": json.dumps(user, separators=(",", ":")),
    }
    if extra:
        fields.update(extra)

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)
