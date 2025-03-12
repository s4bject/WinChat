import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from repositories.user_repository import UserRepository


class FakeScalars:
    def __init__(self, items):
        self.items = items

    def first(self):
        return self.items[0] if self.items else None

    def all(self):
        return self.items


class FakeResult:
    def __init__(self, items):
        self._scalars = FakeScalars(items)

    def scalars(self):
        return self._scalars


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    # Переопределяем методы add, commit и refresh
    db_session.add = AsyncMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock(side_effect=lambda instance: setattr(instance, "id", 1))

    result = await UserRepository.create_user(db_session, name="Alice", email="alice@example.com",
                                              password="password123")

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(result)

    assert isinstance(result, User)
    assert result.email == "alice@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    user = User(id=1, name="Alice", email="alice@example.com", password="hashed_password")

    async def fake_execute(*args, **kwargs):
        return FakeResult([user])

    db_session.execute = AsyncMock(side_effect=fake_execute)

    result = await UserRepository.get_user_by_email(db_session, "alice@example.com")

    db_session.execute.assert_called_once()
    assert result == user
