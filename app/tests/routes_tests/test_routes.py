import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from datetime import datetime
from main import app
from services.message_service import MessageService
from services.user_service import UserService

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_message_history(monkeypatch):
    mock_messages = [
        AsyncMock(id=1, sender_id=1, text="Hello", timestamp=datetime(2024, 3, 12, 12, 0, 0), read=False),
        AsyncMock(id=2, sender_id=2, text="Hi", timestamp=datetime(2024, 3, 12, 12, 1, 0), read=True),
    ]

    async def fake_get_chat_history(db, chat_id, limit=50, offset=0):
        return mock_messages

    monkeypatch.setattr(MessageService, "get_chat_history", fake_get_chat_history)
    monkeypatch.setattr("database.database.get_db", lambda: AsyncMock())

    response = client.get("/history/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["text"] == "Hello"
    assert data[1]["read"] is True


@pytest.mark.asyncio
async def test_register_user(monkeypatch):
    async def fake_user_registration(db, email, name, password):
        return {"email": email, "name": name}

    monkeypatch.setattr(UserService, "user_registration", fake_user_registration)
    monkeypatch.setattr("database.database.get_db", lambda: AsyncMock())

    response = client.post(
        "/register?email=alice@example.com&name=Alice&password=securepass"
    )

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_login_user(monkeypatch):
    fake_user = type("FakeUser", (), {"id": 1, "email": "alice@example.com"})

    async def fake_authenticate_user(db, email, password):
        if email == "alice@example.com" and password == "securepass":
            return fake_user
        raise Exception("Неверные учетные данные")

    async def fake_create_access_token(data):
        return "fake_access_token"

    monkeypatch.setattr(UserService, "authenticate_user", fake_authenticate_user)
    monkeypatch.setattr(UserService, "create_access_token", fake_create_access_token)
    monkeypatch.setattr("database.database.get_db", lambda: AsyncMock())
    response = client.post(
        "/login?email=alice@example.com&password=securepass"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["access_token"] == "fake_access_token"
    assert data["token_type"] == "bearer"
    assert "auth_token" in response.cookies
