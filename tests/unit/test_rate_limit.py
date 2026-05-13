from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def test_rate_limit_returns_429_after_limit():
    settings = get_settings()
    old_enabled = settings.enable_rate_limit
    old_requests = settings.rate_limit_requests
    old_window = settings.rate_limit_window_seconds
    settings.enable_rate_limit = True
    settings.rate_limit_requests = 1
    settings.rate_limit_window_seconds = 60
    try:
        client = TestClient(app)
        payload = {"message": "公司拖欠工资三个月, 我可以离职并要求补偿吗?", "legal_domain": "labor"}
        assert client.post("/legal-qa", json=payload).status_code == 200
        second = client.post("/legal-qa", json=payload)
        assert second.status_code == 429
        assert second.json()["status"] == "rate_limited"
    finally:
        settings.enable_rate_limit = old_enabled
        settings.rate_limit_requests = old_requests
        settings.rate_limit_window_seconds = old_window

