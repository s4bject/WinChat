import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Chat
from repositories.chat_repository import ChatRepository


@pytest.mark.asyncio
async def test_create_chat(db_session: AsyncSession):
    # Переопределим методы add, commit и refresh в фикстуре
    db_session.add = AsyncMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock(side_effect=lambda instance: setattr(instance, "id", 1))

    result = await ChatRepository.create_chat(db_session)

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(result)

    assert isinstance(result, Chat)
    assert result.id == 1


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
async def test_get_chat_by_id(db_session: AsyncSession):
    chat = Chat(id=1)

    async def fake_execute(*args, **kwargs):
        return FakeResult([chat])

    db_session.execute = AsyncMock(side_effect=fake_execute)

    result = await ChatRepository.get_chat_by_id(db_session, 1)

    db_session.execute.assert_called_once()
    assert result == chat
