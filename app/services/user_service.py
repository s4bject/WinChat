import logging
from fastapi import HTTPException
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from dotenv import load_dotenv
import os
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

salt = bcrypt.gensalt()
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('HS256')


class UserService:
    @staticmethod
    async def user_registration(db: AsyncSession, email: str, full_name: str, password: str):
        logger.info(f"Попытка регистрации пользователя с email {email}")
        user = await UserRepository.get_user_by_email(db, email)
        if user:
            logger.error(f"Ошибка регистрации: email {email} уже используется.")
            raise HTTPException(status_code=400, detail="Email уже используется.")
        new_user = await UserRepository.create_user(db, full_name, email, password)
        logger.info(f"Пользователь {email} успешно зарегистрирован.")
        return new_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        logger.info(f"Попытка аутентификации пользователя с email {email}")
        user = await UserRepository.get_user_by_email(db, email)
        if not user:
            logger.error(f"Пользователь с email {email} не найден.")
            raise HTTPException(status_code=400, detail="Пользователь не найден")
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            logger.error(f"Неверный пароль для пользователя с email {email}.")
            raise HTTPException(status_code=400, detail="Неверный пароль")
        logger.info(f"Пользователь с email {email} успешно аутентифицирован.")
        return user

    @staticmethod
    async def create_access_token(data: dict):
        logger.info("Создание токена доступа.")
        to_encode = data.copy()
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("Токен доступа успешно создан.")
        return encoded_jwt
