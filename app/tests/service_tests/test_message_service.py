import pytest
from unittest.mock import AsyncMock, MagicMock
from services.message_service import MessageService
from repositories.message_repository import MessageRepository


@pytest.mark.asyncio
async def test_send_message(db_session):
    MessageRepository.create_message = AsyncMock(return_value=MagicMock(id=1, text='Hello'))

    message = await MessageService.send_message(db_session, 1, 1, "Hello")

    assert message.id == 1
    assert message.text == "Hello"
    MessageRepository.create_message.assert_called_once_with(db_session, 1, 1, "Hello")


@pytest.mark.asyncio
async def test_get_chat_history(db_session):
    MessageRepository.get_chat_messages = AsyncMock(return_value=[{"id": 1, "text": "Hello"}])

    messages = await MessageService.get_chat_history(db_session, 1, limit=10, offset=0)

    assert len(messages) == 1
    assert messages[0]["text"] == "Hello"
    MessageRepository.get_chat_messages.assert_called_once_with(db_session, 1, 10, 0)


@pytest.mark.asyncio
async def test_mark_message_as_read(db_session):
    MessageRepository.mark_as_read = AsyncMock(return_value={"id": 1, "read": True})

    message = await MessageService.mark_message_as_read(db_session, 1)

    assert message["id"] == 1
    assert message["read"] is True
    MessageRepository.mark_as_read.assert_called_once_with(db_session, 1)
