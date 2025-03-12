import json
import logging
from fastapi import WebSocket, APIRouter, Query, Depends
import jwt
from services.message_service import MessageService
from services.chat_service import ChatService
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[dict]] = {}

    async def connect(self, chat_id: int, websocket: WebSocket, user_email: str, db: AsyncSession):
        await websocket.accept()
        await ChatService.check_or_create_chat(db, chat_id)
        history = await MessageService.get_chat_history(db, chat_id)

        logger.info(f"Пользователь {user_email} подключен к чату {chat_id}")

        for msg in history:
            sender_email = msg.sender.email if msg.sender else "Unknown"
            message_data = {
                "action": "new_message",
                "data": {
                    "id": msg.id,
                    "email": sender_email,
                    "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "text": msg.text,
                    "read": msg.read
                }
            }
            await websocket.send_text(json.dumps(message_data))

        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append({"ws": websocket, "email": user_email})
        await self.broadcast_active_users(chat_id)

    def disconnect(self, chat_id: int, websocket: WebSocket):
        if chat_id in self.active_connections:
            self.active_connections[chat_id] = [
                conn for conn in self.active_connections[chat_id] if conn["ws"] != websocket
            ]
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

        logger.info(f"Пользователь с websocket отключен от чата {chat_id}")

    async def broadcast(self, chat_id: int, message: dict):
        message_json = json.dumps(message)
        if chat_id in self.active_connections:
            for conn in list(self.active_connections[chat_id]):
                try:
                    await conn["ws"].send_text(message_json)
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
                    self.active_connections[chat_id].remove(conn)

    async def broadcast_active_users(self, chat_id: int):
        if chat_id in self.active_connections:
            active_users = [conn["email"] for conn in self.active_connections[chat_id]]
            message = {
                "action": "active_users",
                "data": active_users
            }
            await self.broadcast(chat_id, message)


manager = ConnectionManager()


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, token: str = Query(None),
                             db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Попытка подключения пользователя с токеном к чату {chat_id}")
        payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
        user_email = payload.get("email")
        user_id = payload.get("id")

        logger.info(f"Пользователь {user_email} аутентифицирован для чата {chat_id}")
        await manager.connect(chat_id, websocket, user_email, db)

        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                logger.error(f"Ошибка декодирования сообщения от пользователя {user_email} в чате {chat_id}")
                continue

            action = message.get("action")
            if action == "send_message":
                text = message.get("text")
                new_msg = await MessageService.send_message(db, chat_id, user_id, text)

                logger.info(f"Пользователь {user_email} отправил сообщение в чат {chat_id}: {new_msg.text}")

                broadcast_data = {
                    "action": "new_message",
                    "data": {
                        "id": new_msg.id,
                        "email": user_email,
                        "timestamp": new_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "text": new_msg.text,
                        "read": new_msg.read
                    }
                }
                await manager.broadcast(chat_id, broadcast_data)

            elif action == "read_message":
                msg_id = message.get("message_id")
                updated_msg = await MessageService.mark_message_as_read(db, msg_id)
                if updated_msg:
                    broadcast_data = {
                        "action": "message_read",
                        "data": {
                            "id": updated_msg.id,
                            "read": updated_msg.read
                        }
                    }
                    await manager.broadcast(chat_id, broadcast_data)

    except Exception as e:
        logger.error(f"Ошибка при подключении пользователя к чату {chat_id}: {e}")
        await websocket.close()

    finally:
        manager.disconnect(chat_id, websocket)
        if chat_id in manager.active_connections:
            await manager.broadcast_active_users(chat_id)
