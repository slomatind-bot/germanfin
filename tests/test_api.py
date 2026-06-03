"""Тесты API через TestClient FastAPI."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health() -> None:
    """GET /health должен вернуть {"status": "ok"}."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_log() -> None:
    """Создание лога и проверка полей ответа (POST /logs)."""
    payload = {"source": "test", "message": "test message", "level": "info"}
    resp = client.post("/logs", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["source"] == "test"
    assert data["message"] == "test message"
    assert data["level"] == "info"
    assert "id" in data
    assert "timestamp" in data


def test_list_logs() -> None:
    """GET /logs возвращает список с пагинацией."""
    resp = client.get("/logs")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


def test_invalid_level() -> None:
    """Невалидный level → 422."""
    payload = {"source": "test", "message": "x", "level": "critical"}
    resp = client.post("/logs", json=payload)
    assert resp.status_code == 422


def test_get_nonexistent_log() -> None:
    """Запрос несуществующего ID → 404."""
    resp = client.get("/logs/999999")
    assert resp.status_code == 404
