import re
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(?i)authorization\s*:\s*bearer\s+[^,\s]+"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^,\s]+"),
    re.compile(r"(?i)bearer\s+[a-z0-9._\-]+"),
    re.compile(r"sk-[a-zA-Z0-9]{12,}"),
]


def redact_text(text: str | None, max_length: int = 1000) -> str | None:
    if text is None:
        return None
    redacted = text[:max_length]
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def sanitize_payload(payload: Any, max_text_length: int = 1000) -> Any:
    if isinstance(payload, dict):
        sanitized: dict[str, Any] = {}
        for key, value in payload.items():
            if key.lower() in {"authorization", "api_key", "apikey", "token", "password", "secret"}:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_payload(value, max_text_length)
        return sanitized
    if isinstance(payload, list):
        return [sanitize_payload(item, max_text_length) for item in payload]
    if isinstance(payload, str):
        return redact_text(payload, max_text_length)
    return payload
