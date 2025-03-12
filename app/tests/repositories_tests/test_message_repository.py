import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Message
from repositories.message_repository import MessageRepository


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
async def test_create_message(db_session: AsyncSession):
    # Переопределяем методы add, commit и refresh
    db_session.add = AsyncMock()
    db_session.commit = AsyncMock()
    db_session.refresh = AsyncMock(side_effect=lambda instance: setattr(instance, "id", 1))

    result = await MessageRepository.create_message(db_session, chat_id=1, sender_id=1, text="Hello")

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(result)

    assert isinstance(result, Message)
    assert result.text == "Hello"


@pytest.mark.asyncio
async def test_get_chat_messages(db_session: AsyncSession):
    messages = [
        Message(id=1, chat_id=1, sender_id=1, text="Hi"),
        Message(id=2, chat_id=1, sender_id=2, text="Hey")
    ]

    async def fake_execute(*args, **kwargs):
        return FakeResult(messages)

    db_session.execute = AsyncMock(side_effect=fake_execute)

    result = await MessageRepository.get_chat_messages(db_session, chat_id=1)

    db_session.execute.assert_called_once()
    assert result == messages
    assert len(result) == 2
