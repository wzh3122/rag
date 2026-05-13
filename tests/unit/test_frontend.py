from fastapi.testclient import TestClient

from app.main import app


def test_frontend_index_is_served():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "大陆法律 RAG 助手" in response.text
    assert "/static/app.js" in response.text


def test_frontend_assets_are_served():
    client = TestClient(app)
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert ".composer" in response.text
