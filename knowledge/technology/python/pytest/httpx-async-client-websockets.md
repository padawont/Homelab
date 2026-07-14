---
title: "WebSocket Testing with httpx"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - httpx
  - websocket
  - async
  - testing
  - websockets-library
sources:
  - url: "https://websockets.readthedocs.io/"
    title: "websockets Library Documentation"
  - url: "https://www.python-httpx.org/compatibility/"
    title: "httpx — Protocol Compatibility"
  - url: "https://www.starlette.io/testclient/#testing-websocket-sessions"
    title: "Starlette — Testing WebSocket Sessions"
last_audit_date: 2026-06-10
---

# WebSocket Testing with httpx

**httpx does NOT have built-in WebSocket client support.** Methods like `ws_connect`, `send_json`, `receive_json`, `send_text`, `receive_bytes`, and `close` shown in earlier versions of this document **do not exist** in the httpx library.

For WebSocket testing you need a dedicated WebSocket client library, most commonly the [`websockets`](https://websockets.readthedocs.io/) library.

## Why httpx Has No WebSocket Client

httpx is an HTTP client library. The HTTP/1.1 and HTTP/2 protocols do not define the client-side WebSocket API — that is handled by the WebSocket protocol (RFC 6455), which is a separate TCP-based protocol that only uses HTTP for its initial upgrade handshake. httpx explicitly documents that it does not support WebSocket connections.

## Using the `websockets` Library for Testing

The [`websockets`](https://websockets.readthedocs.io/) library is the de facto standard for WebSocket client/server testing in Python.

### Basic WebSocket Test (Live Server)

```python
import pytest
from websockets import connect

@pytest.mark.asyncio
async def test_websocket():
    async with connect("ws://localhost:8000/ws") as websocket:
        await websocket.send('{"type": "ping"}')
        response = await websocket.recv()
        assert response == '{"type": "pong"}'
```

### JSON Messages

```python
import json

@pytest.mark.asyncio
async def test_websocket_json():
    async with connect("ws://localhost:8000/ws") as websocket:
        # Send JSON
        await websocket.send(json.dumps({"action": "subscribe"}))

        # Receive JSON
        response = json.loads(await websocket.recv())
        assert response["status"] == "ok"
```

### Sending and Receiving Different Types

```python
async with connect("ws://localhost:8000/ws") as ws:
    # Text
    await ws.send("hello")
    msg = await ws.recv()

    # JSON (serialize/deserialize manually)
    import json
    await ws.send(json.dumps({"action": "subscribe"}))
    msg = json.loads(await ws.recv())

    # Bytes
    await ws.send(b"data")
    msg = await ws.recv()
```

### Multiple Messages

```python
@pytest.mark.asyncio
async def test_websocket_chat():
    async with connect("ws://localhost:8000/chat") as ws:
        import json
        await ws.send(json.dumps({"user": "alice", "msg": "Hi"}))
        await ws.send(json.dumps({"user": "bob", "msg": "Hello"}))
        resp1 = json.loads(await ws.recv())
        resp2 = json.loads(await ws.recv())
        assert resp1["msg"] == "Hi"
        assert resp2["msg"] == "Hello"
```

### Close Handling

```python
@pytest.mark.asyncio
async def test_websocket_close():
    async with connect("ws://localhost:8000/ws") as ws:
        import json
        await ws.send(json.dumps({"type": "close"}))
        # Connection closes automatically when exiting the context manager
    # Use close_timeout for graceful shutdown:
    # await ws.close(code=1000)
```

## Testing ASGI WebSockets Without a Live Server

If you are testing a FastAPI or Starlette app and do not want to run a live server, use **Starlette's `TestClient`**, which has built-in WebSocket testing support:

```python
from starlette.testclient import TestClient
from myapp import app

def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"type": "ping"})
        data = websocket.receive_json()
        assert data["type"] == "pong"
```

Key differences from httpx:
- `TestClient` is **synchronous** — no `async`/`await` needed.
- `TestClient.websocket_connect()` returns a `WebSocketTestSession` with methods like `send_json()`, `receive_json()`, `send_text()`, `receive_text()`, `send_bytes()`, `receive_bytes()`, and `close()`.
- No live server required — the ASGI app is called directly.
- This is the recommended approach for FastAPI/Starlette WebSocket tests.

> **Note:** `httpx.AsyncClient` + `ASGITransport` (used for HTTP testing) **does not** support WebSocket connections. Use Starlette's `TestClient` when you need in-process WebSocket testing, or the `websockets` library against a running server.

See [httpx-async-client-fastapi](./httpx-async-client-fastapi.md) for the base HTTP-only setup using `AsyncClient` with `ASGITransport`.
