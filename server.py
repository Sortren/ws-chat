from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from managers import PublicConnectionManager, PrivateConnectionManager


app = FastAPI()

public_manager = PublicConnectionManager()
private_manager = PrivateConnectionManager()


@app.websocket("/chat/public")
async def public_chat(websocket: WebSocket):
    await public_manager.connect(websocket)
    await public_manager.broadcast(f"Someone joined the chat!")

    try:
        while True:
            data = await websocket.receive_json()
            await public_manager.broadcast(f"{data.get('username')}> {data.get('message')}")
    except WebSocketDisconnect:
        public_manager.disconnect(websocket)
        await public_manager.broadcast(f"Someone left the chat!")


@app.websocket("/chat/private")
async def private_chat(websocket: WebSocket):
    await private_manager.connect(websocket)
    room_id = private_manager.find_room_id(websocket)
    await private_manager.broadcast('Someone joined the chat!', room_id)

    try:
        while True:
            data = await websocket.receive_json()
            await private_manager.broadcast(f"{data.get('username')}> {data.get('message')}", room_id)
    except WebSocketDisconnect:
        private_manager.disconnect(websocket)
        await private_manager.broadcast('Someone left the chat!', room_id)
