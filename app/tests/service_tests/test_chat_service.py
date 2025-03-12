import pytest
from unittest.mock import AsyncMock, MagicMock
from services.chat_service import ChatService
from repositories.chat_repository import ChatRepository


@pytest.mark.asyncio
async def test_create_chat(db_session):
    ChatRepository.create_chat = AsyncMock(return_value=MagicMock(id=1))

    chat = await ChatService.create_chat(db_session)

    assert chat.id == 1
    ChatRepository.create_chat.assert_called_once_with(db_session)


@pytest.mark.asyncio
async def test_check_or_create_chat_existing(db_session):
    ChatRepository.get_chat_by_id = AsyncMock(return_value={"id": 1})

    result = await ChatService.check_or_create_chat(db_session, 1)

    assert result is True
    ChatRepository.get_chat_by_id.assert_called_once_with(db_session, 1)


@pytest.mark.asyncio
async def test_check_or_create_chat_not_existing(db_session):
    ChatRepository.get_chat_by_id = AsyncMock(return_value=None)
    ChatService.create_chat = AsyncMock(return_value={"id": 2})

    result = await ChatService.check_or_create_chat(db_session, 99)

    assert result["id"] == 2
    ChatRepository.get_chat_by_id.assert_called_once_with(db_session, 99)
    ChatService.create_chat.assert_called_once_with(db_session)
