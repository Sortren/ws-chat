from abc import ABC, abstractmethod
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect


app = FastAPI()


class ConnectionManager(ABC):
    def __init__(self):
        self.active_connections = []

    @abstractmethod
    async def connect(self, websocket: WebSocket):
        pass

    @abstractmethod
    def disconnect(self, websocket: WebSocket):
        pass

    @abstractmethod
    async def broadcast(self, message: str):
        pass


class PublicConnectionManager(ConnectionManager):
    '''
    Stands for connection to the PUBLIC chat room
    without limiting amount of connected clients
    '''

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class PrivateConnectionManager(ConnectionManager):
    '''
    Stands for connection to the PRIVATE chat room
    with limiting amount of connected clients to 2 by each room
    '''

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        if len(self.active_connections) == 0 or len(self.active_connections[-1]) == 2:
            self.active_connections.append([websocket])
        elif len(self.active_connections[-1]) < 2:
            self.active_connections[-1].append(websocket)

    def disconnect(self, websocket: WebSocket):
        for index, room in enumerate(self.active_connections):
            if websocket in room:
                self.active_connections[index].remove(websocket)
                if len(room) == 0:
                    self.active_connections.remove(room)


public_manager = PublicConnectionManager()


@app.websocket("/chat/public-room")
async def public_room(websocket: WebSocket):
    await public_manager.connect(websocket)
    await public_manager.broadcast(f"Someone joined the chat!")

    try:
        while True:
            data = await websocket.receive_json()
            await public_manager.broadcast(f"{data.get('username')}> {data.get('message')}")
    except WebSocketDisconnect:
        public_manager.disconnect(websocket)
        await public_manager.broadcast(f"Someone left the chat!")