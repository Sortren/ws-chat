
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from managers.private import PrivateConnectionManager
from managers.public import PublicConnectionManager


router = APIRouter()

public_manager = PublicConnectionManager()
private_manager = PrivateConnectionManager()


@router.websocket("/public")
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
        await public_manager.broadcast({"message": "Someone left the chat!"})


@router.websocket("/private")
async def private_chat(websocket: WebSocket):
    await private_manager.connect(websocket)
    client_room_id = private_manager.find_client_room_id(websocket)
    await private_manager.greeting_broadcast(websocket, client_room_id)

    try:
        while True:
            data = await websocket.receive_json()
            await private_manager.broadcast(data, client_room_id)
    except WebSocketDisconnect:
        private_manager.disconnect(websocket)
        await private_manager.broadcast({"message": "Someone left the chat!"}, client_room_id)
