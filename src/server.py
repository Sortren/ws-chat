from fastapi import FastAPI
from routers import chat

app = FastAPI()
app.include_router(chat.router, prefix="/chat")
