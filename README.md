# Chat {WebSocket} - FastAPI
Basically a websocket that allows to connect to the public or private (random generated) chat.

## Technologies used:

<img align = "left" alt = "Python" width = "26px" src = "https://user-images.githubusercontent.com/79079000/118809383-da383580-b8aa-11eb-9b90-b36be1ebd84a.png" />
<img align = "left" alt = "FastAPI" width = "26px" src = "https://user-images.githubusercontent.com/79079000/125871360-23548c10-f1f7-4b42-ad6b-ed8eaec20490.png" />
<img align = "left" alt = "Git" width = "26px" src = "https://user-images.githubusercontent.com/79079000/118809398-e1f7da00-b8aa-11eb-809d-bef2203df08d.png" />

<br />

----
## How to build the project:
1) Create virtual environment in your workdir by typing this command in your terminal (RECOMMENDED)
### `$virtualenv venv`
2) Activate venv
### `$source venv/bin/activate`
3) Install required python modules from requirements.txt file
### `$pip install -r requirements.txt`
4) Change current workdir to src
### `$cd src`
5) To run the server
### `$uvicorn server:app --reload`

### DISCLAIMER
If running an uvicorn invokes an error like "no module named 'fastapi'" you likely gonna have to install fastapi globally on your python env,
to do this, just type in your terminal
### `$pip install fastapi`
problem solved 😎

----
## Main logic

The chats are split to the two endpoints, one is 
```python
@app.websocket("/chat/public")
async def public_chat(websocket: WebSocket)
```
Which stands for connection to the public chat

The other is:
```python
@app.websocket("/chat/private")
async def private_chat(websocket: WebSocket)
```
Which stands for connection to the private, random generated chat

----

In both cases the client sends a json that looks like this:
```json
{
  "username": "example_username",
  "message": "example_message"
}
```

Received json by the socket is used for sending a message to the chat room with username and message provided before.
Messages are being transported amongs clients accordingly to the chosen endpoint.
Example output:
```text
example_username> example_message 
```
----
### Disclaimer about PrivateConnectionManager
Main logic assigned to the private, random chat connection has been done quite differently as it might be.
To get all the thing straighten out: <br>
1) Client tries to connect via socket
2) If there is no such private room, creates one and assign client to it
3) If there is bunch of private rooms but all of them contains exactly two clients (meaning that it is full), creates the new room and assign the client to it
4) If there is couple of private rooms that contains exactly one client (so one slot is free), counts all of the rooms that match the condition, gets a random choice from all of the free rooms and assign client to the chosen one
5) Messages being broadcasted amongs private rooms
