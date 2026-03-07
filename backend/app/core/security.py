from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta


HASH_NAME = "sha256"
ITERATIONS = 260_000
SALT_BYTES = 16


def hash_password(password: str, salt: str | None = None) -> str:
    resolved_salt = salt or secrets.token_hex(SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        resolved_salt.encode("utf-8"),
        ITERATIONS,
    ).hex()
    return f"{resolved_salt}${password_hash}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        salt, expected_hash = encoded_hash.split("$", maxsplit=1)
    except ValueError:
        return False

    candidate = hash_password(password, salt=salt).split("$", maxsplit=1)[1]
    return hmac.compare_digest(candidate, expected_hash)


def generate_access_token() -> str:
    return secrets.token_urlsafe(36)


def calculate_expiry(hours: int) -> datetime:
    return datetime.now() + timedelta(hours=hours)
