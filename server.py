from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect


app = FastAPI()


class PublicConnectionManager:
    '''
    Stands for connection to the public chat room
    without limiting amount of connected clients
    '''

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


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
