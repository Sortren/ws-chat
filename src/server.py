from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from managers import PublicConnectionManager, PrivateConnectionManager

app = FastAPI()

public_manager = PublicConnectionManager()
private_manager = PrivateConnectionManager()


@app.websocket("/chat/public")
async def public_chat(websocket: WebSocket):
    await public_manager.connect(websocket)
    await public_manager.counter_broadcast()
    await public_manager.greeting_broadcast(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await public_manager.broadcast(data)
    except WebSocketDisconnect:
        await public_manager.disconnect(websocket)
        await public_manager.counter_broadcast()
        await public_manager.broadcast(f"Someone left the chat!")


@app.websocket("/chat/private")
async def private_chat(websocket: WebSocket):
    await private_manager.connect(websocket)
    current_room_id = private_manager.find_client_room(websocket)
    await private_manager.greeting_broadcast(websocket, current_room_id)

    try:
        while True:
            data = await websocket.receive_json()
            await private_manager.broadcast(data, current_room_id)
    except WebSocketDisconnect:
        private_manager.disconnect(websocket)
        await private_manager.broadcast('Someone left the chat!', current_room_id)
