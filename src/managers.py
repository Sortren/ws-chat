from abc import ABC, abstractmethod
from fastapi import WebSocket
import random
import string


class ConnectionManager(ABC):
    @abstractmethod
    async def connect(self, websocket: WebSocket):
        pass

    @abstractmethod
    def disconnect(self, websocket: WebSocket):
        pass

    @abstractmethod
    async def broadcast(self, message: str, room_id=None):
        pass

    @abstractmethod
    async def greeting_broadcast(self, websocket: WebSocket, room_id: str):
        pass

    async def greeting_condition(self, websocket: WebSocket, client: WebSocket):
        if client is websocket:
            await client.send_text("Welcome to the chat room!")
        else:
            await client.send_text("Someone joined the chat!")


class PublicConnectionManager(ConnectionManager):
    '''
    Stands for connection to the PUBLIC chat room
    without limiting amount of connected clients
    '''

    def __init__(self):
        self.public_chat = []

    async def send_counter(self):
        '''
        Sends the number of current active clients in the public chat
        '''
        for client in self.public_chat:
            await client.send_text(str(len(self.public_chat)))

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.public_chat.append(websocket)
        await self.send_counter()

    async def disconnect(self, websocket: WebSocket):
        self.public_chat.remove(websocket)
        await self.send_counter()


class PrivateConnectionManager(ConnectionManager):
    '''
    Stands for connection to the PRIVATE chat room
    with limiting amount of connected clients to 2 by each room
    '''

    def __init__(self):
        self._private_rooms = {}

    def _generate_room(self, websocket: WebSocket):
        '''
        Generates new room with unique string id 
        and inserts incoming client
        '''
        room_id = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(12))

        self._private_rooms[room_id] = [websocket]

    def _free_rooms(self):
        '''
        Returns IDs of the free rooms in a list,
        Room is free when there is only one client,
        so one slot is free for someone else
        '''
        free_rooms = []
        for id, clients in self._private_rooms.items():
            if len(clients) == 1:
                free_rooms.append(id)

        return free_rooms

    def find_client_room(self, websocket: WebSocket):
        '''
        Returns the id of the room where the client
        is connected to
        '''
        for id, clients in self._private_rooms.items():
            if websocket in clients:
                return id

    async def connect(self, websocket: WebSocket):
        '''
        Connecting clients to the private rooms with size of two
        works like a queue, the next client in queue will put
        to a random free room, if all of the rooms are full,
        creates new one
        '''
        await websocket.accept()
        free_rooms = self._free_rooms()

        if free_rooms:
            room_id = random.choice(free_rooms)
            self._private_rooms[room_id].append(websocket)
        else:
            self._generate_room(websocket)

    def disconnect(self, websocket: WebSocket):
        client_room = self.find_client_room(websocket)

        if not client_room:
            return

        self._private_rooms[client_room].remove(websocket)

        if not len(self._private_rooms[client_room]):
            self._private_rooms.pop(client_room)

    async def broadcast(self, message: str, room_id):
        try:
            for client in self._private_rooms[room_id]:
                await client.send_text(message)
        except KeyError:
            '''
            Exception raised when server tries
            to send a message to non existing room,
            ex. when everyone left the current room
            '''
            pass

    async def greeting_broadcast(self, websocket: WebSocket, room_id: str):
        '''
        Different message will be send depending
        on the client
        '''
        try:
            for client in self._private_rooms[room_id]:
                await super().greeting_condition(websocket, client)

        except KeyError:
            pass
