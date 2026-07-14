---
title: "WebSocket — Introduction"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - websockets
sources:
  - url: "https://fastapi.tiangolo.com/advanced/websockets/"
    title: "FastAPI Docs — WebSockets"
last_audit_date: 2026-06-09
---

# WebSocket — Introduction

Bi-directional real-time communication with WebSockets:

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message was: {data}")
```

## Key methods

| Method | Purpose |
|---|---|
| `await websocket.accept()` | Accept the WebSocket connection |
| `await websocket.receive_text()` | Receive a text message |
| `await websocket.receive_bytes()` | Receive binary data |
| `await websocket.receive_json()` | Receive and parse JSON |
| `await websocket.send_text(data)` | Send text |
| `await websocket.send_bytes(data)` | Send binary |
| `await websocket.send_json(data)` | Send JSON |
| `await websocket.close()` | Close the connection |

## Client example (JavaScript)

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");
ws.onopen = () => ws.send("Hello!");
ws.onmessage = (event) => console.log(event.data);
```

## WebSocket with path params

```python
@app.websocket("/chat/{room_id}")
async def chat_room(websocket: WebSocket, room_id: str):
    await websocket.accept()
    await websocket.send_text(f"Connected to room: {room_id}")
    ...
```

See [websockets-managing-connections.md](./websockets-managing-connections.md) for connection managers and [websockets-broadcast.md](./websockets-broadcast.md) for broadcasting.
