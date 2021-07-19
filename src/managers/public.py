from fastapi import WebSocket

from .connection import ConnectionManager


class PublicConnectionManager(ConnectionManager):
    '''
    Stands for connection to the PUBLIC chat room
    without limiting amount of connected clients
    '''

    def __init__(self):
        self.public_chat = []

    async def counter_broadcast(self):
        '''
        Sends the number of current active clients in the public chat
        '''
        counter = str(len(self.public_chat))

        for client in self.public_chat:
            await client.send_json({"counter": counter})

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.public_chat.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.public_chat.remove(websocket)

    async def broadcast(self, data: dict):
        for client in self.public_chat:
            await client.send_json(data)

    async def greeting_broadcast(self, websocket: WebSocket):
        for client in self.public_chat:
            await super().greeting_condition(websocket, client)
