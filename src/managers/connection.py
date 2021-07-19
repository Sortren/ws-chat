from abc import ABC, abstractmethod
from fastapi import WebSocket


class ConnectionManager(ABC):
    @abstractmethod
    async def connect(self, websocket: WebSocket):
        pass

    @abstractmethod
    def disconnect(self, websocket: WebSocket):
        pass

    @abstractmethod
    async def broadcast(self, message: dict):
        pass

    @abstractmethod
    async def greeting_broadcast(self, websocket: WebSocket):
        pass

    async def greeting_condition(self, websocket: WebSocket, client: WebSocket):
        if client is websocket:
            await client.send_json({"greeting": "Welcome to the chat room!"})
        else:
            await client.send_json({"greeting": "Someone joined the chat!"})
