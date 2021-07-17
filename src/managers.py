from abc import ABC, abstractmethod
from fastapi import WebSocket
import random
import string


class ConnectionManager(ABC):
    active_connections = []

    @abstractmethod
    async def connect(self, websocket: WebSocket):
        pass

    @abstractmethod
    def disconnect(self, websocket: WebSocket):
        pass

    async def broadcast(self, message: str, room_id=None):
        '''
        Broadcasting messages appropriate for public/private chat room
        '''
        try:
            for connection in self.active_connections if room_id is None else self.active_connections[room_id]:
                await connection.send_text(message)
        except IndexError:
            # Error occurs if the app tries to send a broadcast to an empty room
            pass

    async def greeting_broadcast(self, websocket: WebSocket, room_id=None):
        '''
        Greeting message broadcasting depending on the client 
        that is currently connected
        '''
        try:
            for connection in self.active_connections if room_id is None else self.active_connections[room_id]:
                if connection is websocket:
                    await connection.send_text("Welcome to the chat room!")
                else:
                    await connection.send_text("Someone joined the chat!")
        except IndexError:
            pass


class PublicConnectionManager(ConnectionManager):
    '''
    Stands for connection to the PUBLIC chat room
    without limiting amount of connected clients
    '''
    async def send_counter(self):
        '''
        Sends the number of current active clients in the public chat
        '''
        for connection in self.active_connections:
            await connection.send_text(str(len(self.active_connections)))

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_counter()

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
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

    def _find_client_room(self, websocket: WebSocket):
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
        client_room = self._find_client_room(websocket)
        if not client_room:
            return

        self._private_rooms[client_room].remove(websocket)
