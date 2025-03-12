from fastapi import FastAPI
from api.websocket import router as websocket_router
from api.routes import router as api_router

app = FastAPI()

app.include_router(websocket_router)
app.include_router(api_router)
