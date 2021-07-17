from abc import ABC, abstractmethod
from fastapi import WebSocket
from random import choice


class ConnectionManager(ABC):
    def __init__(self):
        self.active_connections = []

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
            for connection in (self.active_connections[room_id] if room_id else self.active_connections):
                await connection.send_text(message)
        except IndexError:
            # Error occurs if the app tries to send a broadcast to an empty room
            pass

    async def greeting_broadcast(self, websocket: WebSocket, room_id=None):
        '''
        Greeting message broadcasting depending on the client 
        that is currently connected
        '''
        for connection in (self.active_connections[room_id] if room_id else self.active_connections):
            if connection == websocket:
                await connection.send_text("Welcome to the chat room!")
            else:
                await connection.send_text("Someone joined the chat!")


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


class PrivateConnectionManager(ConnectionManager):
    '''
    Stands for connection to the PRIVATE chat room
    with limiting amount of connected clients to 2 by each room
    '''

    def current_room_id(self, websocket: WebSocket) -> int:
        '''
        Returns the index of the room where the current client is connected to
        '''
        for index, room in enumerate(self.active_connections):
            if websocket in room:
                return index

    def free_room_id(self) -> int:
        '''
        Returns the index of the random room where only one client is located
        '''
        free_rooms = list(
            filter(
                lambda client: len(client) == 1, self.active_connections
            )
        )
        random_free_room = choice(free_rooms)
        return self.active_connections.index(random_free_room)

    def are_rooms_full(self) -> bool:
        '''
        Check if all of the rooms are fullfilled by clients
        '''
        for room in self.active_connections:
            if len(room) < 2:
                return False
        return True

    async def connect(self, websocket: WebSocket):
        '''
        Connecting clients to the private rooms with size of 2
        Works like a queue, the next client in queue will be
        paired with client with an empty slot in a room
        '''

        await websocket.accept()

        if len(self.active_connections) == 0 or self.are_rooms_full():
            self.active_connections.append([websocket])
        else:
            self.active_connections[self.free_room_id()].append(websocket)

    def disconnect(self, websocket: WebSocket):
        for index, room in enumerate(self.active_connections):
            if websocket in room:
                self.active_connections[index].remove(websocket)
                if len(room) == 0:
                    self.active_connections.remove(room)
