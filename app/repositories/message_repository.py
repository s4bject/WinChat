from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Message
from sqlalchemy.orm import joinedload


class MessageRepository:
    @staticmethod
    async def create_message(db: AsyncSession, chat_id: int, sender_id: int, text: str):
        new_message = Message(chat_id=chat_id, sender_id=sender_id, text=text)
        db.add(new_message)
        await db.commit()
        await db.refresh(new_message)
        return new_message

    @staticmethod
    async def get_chat_messages(db: AsyncSession, chat_id: int, limit: int = 50, offset: int = 0):
        result = await db.execute(
            select(Message)
            .options(joinedload(Message.sender))
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def mark_as_read(db: AsyncSession, message_id: int):
        result = await db.execute(select(Message).where(Message.id == message_id))
        message = result.scalars().first()
        if message:
            message.read = True
            await db.commit()
            await db.refresh(message)
        return message
