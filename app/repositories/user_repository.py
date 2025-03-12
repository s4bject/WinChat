from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import bcrypt
from database.models import User

salt = bcrypt.gensalt()


class UserRepository:

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, name: str, email: str, password: str):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        new_user = User(name=name, email=email, password=hashed_password.decode('utf-8'))
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
