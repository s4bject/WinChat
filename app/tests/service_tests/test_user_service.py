import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
import bcrypt
import jwt
from services.user_service import UserService
from repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_user_registration(db_session):
    UserRepository.get_user_by_email = AsyncMock(return_value=None)
    UserRepository.create_user = AsyncMock(return_value={"id": 1, "email": "test@example.com"})

    user = await UserService.user_registration(db_session, "test@example.com", "Test User", "password123")

    assert user["id"] == 1
    UserRepository.get_user_by_email.assert_called_once_with(db_session, "test@example.com")
    UserRepository.create_user.assert_called_once_with(db_session, "Test User", "test@example.com", "password123")


@pytest.mark.asyncio
async def test_user_registration_email_taken(db_session):
    UserRepository.get_user_by_email = AsyncMock(return_value={"id": 1})

    with pytest.raises(HTTPException) as exc_info:
        await UserService.user_registration(db_session, "test@example.com", "Test User", "password123")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email уже используется."
    UserRepository.get_user_by_email.assert_called_once_with(db_session, "test@example.com")


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session, monkeypatch):
    hashed_password = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    UserRepository.get_user_by_email = AsyncMock(
        return_value=MagicMock(id=1, email="test@example.com", password=hashed_password))

    user = await UserService.authenticate_user(db_session, "test@example.com", "password123")

    assert user.id == 1
    UserRepository.get_user_by_email.assert_called_once_with(db_session, "test@example.com")


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(db_session):
    UserRepository.get_user_by_email = AsyncMock(
        return_value=MagicMock(id=1, email="test@example.com", password=bcrypt.hashpw("wrongpass".encode("utf-8"),
                                                                                      bcrypt.gensalt()).decode("utf-8")))

    with pytest.raises(HTTPException) as exc_info:
        await UserService.authenticate_user(db_session, "test@example.com", "password123")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Неверный пароль"


@pytest.mark.asyncio
async def test_authenticate_user_not_found(db_session):
    UserRepository.get_user_by_email = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await UserService.authenticate_user(db_session, "test@example.com", "password123")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Пользователь не найден"


@pytest.mark.asyncio
async def test_create_access_token(monkeypatch):
    fake_jwt = "fake.token.jwt"
    monkeypatch.setattr(jwt, "encode", lambda data, key, algorithm: fake_jwt)

    token = await UserService.create_access_token({"sub": "test@example.com"})

    assert token == fake_jwt
