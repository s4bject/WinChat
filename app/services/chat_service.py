import logging
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.chat_repository import ChatRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChatService:
    @staticmethod
    async def create_chat(db: AsyncSession):
        logger.info("Попытка создать новый чат.")
        chat = await ChatRepository.create_chat(db)
        if chat:
            logger.info(f"Чат успешно создан с ID: {chat.id}")
        else:
            logger.error("Не удалось создать чат.")
        return chat

    @staticmethod
    async def check_or_create_chat(db: AsyncSession, chat_id: int):
        logger.info(f"Проверка существования чата с ID: {chat_id}")
        chat = await ChatRepository.get_chat_by_id(db, chat_id)
        if chat:
            logger.info(f"Чат с ID {chat_id} существует.")
            return True
        else:
            logger.info(f"Чат с ID {chat_id} не найден. Создание нового чата.")
            return await ChatService.create_chat(db)
