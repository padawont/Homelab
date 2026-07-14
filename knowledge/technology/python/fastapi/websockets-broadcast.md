---
title: "WebSocket — Broadcasting"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - websockets
sources:
  - url: "https://fastapi.tiangolo.com/advanced/websockets/#handling-multiple-clients"
    title: "FastAPI Docs — Broadcasting"
last_audit_date: 2026-06-09
---

# WebSocket — Broadcasting

Broadcast messages to all connected WebSocket clients:

```python
from fastapi import FastAPI, WebSocket
from typing import list

app = FastAPI()


class Broadcaster:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}

    async def join(self, room: str, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(room, []).append(websocket)

    def leave(self, room: str, websocket: WebSocket):
        self.rooms[room].remove(websocket)
        if not self.rooms[room]:
            del self.rooms[room]

    async def broadcast_to_room(self, room: str, message: str):
        for ws in self.rooms.get(room, []):
            try:
                await ws.send_text(message)
            except Exception:
                self.leave(room, ws)


broadcaster = Broadcaster()


@app.websocket("/chat/{room}")
async def chat(websocket: WebSocket, room: str):
    await broadcaster.join(room, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcaster.broadcast_to_room(room, f"[{room}] {data}")
    except Exception:
        broadcaster.leave(room, websocket)
```

## Broadcasting with JSON

```python
await broadcaster.broadcast_to_room(
    room,
    json.dumps({"user": client_id, "message": data}),
)
```

## Handling failed sends

Use try/except in the broadcast loop to remove disconnected clients gracefully.

## Multi-worker broadcasting

For multi-process deployments, use:
- Redis pub/sub
- RabbitMQ
- WebSocket gateways (Pusher, Ably, etc.)

See [websockets-managing-connections.md](./websockets-managing-connections.md) for connection management.
