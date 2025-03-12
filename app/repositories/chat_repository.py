from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Chat


class ChatRepository:
    @staticmethod
    async def create_chat(db: AsyncSession):
        new_chat = Chat()
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)
        return new_chat

    @staticmethod
    async def get_chat_by_id(db: AsyncSession, chat_id: int):
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalars().first()
