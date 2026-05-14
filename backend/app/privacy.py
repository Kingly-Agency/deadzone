from __future__ import annotations

import hashlib
import hmac


def capture_scoped_token(raw_identifier: str, *, salt: str, trace_id: str) -> str:
    digest = hmac.new(
        f"{salt}:{trace_id}".encode("utf-8"),
        raw_identifier.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:16]
