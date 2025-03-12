from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from pydantic import EmailStr, Field
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
import logging

from services.message_service import MessageService
from services.user_service import UserService
from database.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.get("/history/{chat_id}", response_model=List[dict])
async def get_message_history(chat_id: int, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    logger.info(f"Получен запрос на историю сообщений для чата {chat_id} с лимитом {limit} и смещением {offset}")

    try:
        messages = await MessageService.get_chat_history(db, chat_id, limit, offset)
        logger.info(f"Найдено {len(messages)} сообщений для чата {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка при получении истории сообщений для чата {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении истории сообщений")

    return [
        {
            "message_id": message.id,
            "sender_id": message.sender_id,
            "text": message.text,
            "timestamp": message.timestamp.isoformat(),
            "read": message.read
        }
        for message in messages
    ]


@router.post("/register")
async def register_user(
        email: Annotated[EmailStr, Field(max_length=255)],
        name: Annotated[str, Field(max_length=255)],
        password: Annotated[str, Field(min_length=4, max_length=255)],
        db: AsyncSession = Depends(get_db)
):
    logger.info(f"Регистрация нового пользователя: {email}, {name}")

    try:
        result = await UserService.user_registration(db, email, name, password)
        logger.info(f"Пользователь {email} успешно зарегистрирован.")
        return result
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя {email}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при регистрации пользователя")


@router.post("/login")
async def login_user(
        email: Annotated[EmailStr, Field(max_length=255)],
        password: Annotated[str, Field(min_length=4, max_length=255)],
        response: Response,
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"Попытка входа пользователя с email {email}")

    try:
        user = await UserService.authenticate_user(db, email, password)
        logger.info(f"Пользователь {email} успешно аутентифицирован.")
    except Exception as e:
        logger.error(f"Ошибка аутентификации для пользователя {email}: {e}")
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    access_token = await UserService.create_access_token(
        data={"email": user.email, "id": user.id}
    )
    response.set_cookie(key="auth_token", value=access_token, httponly=False)
    logger.info(f"Токен доступа для пользователя {email} успешно создан.")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    logger.info("Запрос на получение страницы чата")
    return templates.TemplateResponse("chat.html", {"request": request})
