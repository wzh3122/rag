from app.utils.security import redact_text, sanitize_payload


def test_redact_text_hides_api_key_like_values():
    text = "Authorization: Bearer abcdef123456 API_KEY=sk-testsecret123456"
    redacted = redact_text(text)
    assert "abcdef123456" not in redacted
    assert "sk-testsecret123456" not in redacted


def test_sanitize_payload_hides_sensitive_keys():
    payload = {"headers": {"Authorization": "Bearer abc"}, "api_key": "secret", "message": "hello"}
    sanitized = sanitize_payload(payload)
    assert sanitized["headers"]["Authorization"] == "[REDACTED]"
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["message"] == "hello"

