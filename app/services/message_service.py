import logging
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.message_repository import MessageRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MessageService:
    @staticmethod
    async def send_message(db: AsyncSession, chat_id: int, sender_id: int, text: str):
        logger.info(f"Отправка сообщения от пользователя {sender_id} в чат {chat_id}. Текст: {text}")
        message = await MessageRepository.create_message(db, chat_id, sender_id, text)
        if message:
            logger.info(f"Сообщение успешно отправлено с ID: {message.id}")
        else:
            logger.error("Не удалось отправить сообщение.")
        return message

    @staticmethod
    async def get_chat_history(db: AsyncSession, chat_id: int, limit: int = 50, offset: int = 0):
        logger.info(f"Получение истории чата {chat_id} с лимитом {limit} и смещением {offset}")
        messages = await MessageRepository.get_chat_messages(db, chat_id, limit, offset)
        logger.info(f"Найдено {len(messages)} сообщений для чата {chat_id}.")
        return messages

    @staticmethod
    async def mark_message_as_read(db: AsyncSession, message_id: int):
        logger.info(f"Отметка сообщения {message_id} как прочитанное.")
        updated_message = await MessageRepository.mark_as_read(db, message_id)
        if updated_message:
            logger.info(f"Сообщение {message_id} успешно отмечено как прочитанное.")
        else:
            logger.error(f"Не удалось отметить сообщение {message_id} как прочитанное.")
        return updated_message
