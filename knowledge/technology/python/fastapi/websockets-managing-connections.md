---
title: "WebSocket — Connection Manager"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - websockets
sources:
  - url: "https://fastapi.tiangolo.com/advanced/websockets/#handling-multiple-clients"
    title: "FastAPI Docs — Handling Multiple Clients"
last_audit_date: 2026-06-09
---

# WebSocket — Connection Manager

Manage multiple WebSocket connections:

```python
from fastapi import FastAPI, WebSocket
from typing import List

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client {client_id} says: {data}")
    except Exception:
        manager.disconnect(websocket)
```

## Thread safety

`ConnectionManager` is not thread-safe. For multi-worker deployments, use a shared state backend (Redis pub/sub). The basic pattern works for single-process servers.

## Clean disconnection

Always wrap the receive loop in try/except to handle disconnections gracefully.

See [websockets-intro.md](./websockets-intro.md) for WebSocket basics and [websockets-broadcast.md](./websockets-broadcast.md) for broadcast patterns.
