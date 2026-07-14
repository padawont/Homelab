---
title: "Testing — WebSocket Endpoints"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - websockets
sources:
  - url: "https://fastapi.tiangolo.com/advanced/testing-websockets/"
    title: "FastAPI Docs — Testing WebSockets"
last_audit_date: 2026-06-09
---

# Testing — WebSocket Endpoints

Test WebSocket endpoints with `TestClient`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_websocket():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Hello, server!")
        data = websocket.receive_text()
        assert data == "Message was: Hello, server!"
```

## Sending and receiving

```python
def test_websocket_json():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"action": "ping"})
        response = websocket.receive_json()
        assert response == {"action": "pong"}
```

## Testing disconnection

```python
def test_websocket_close():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("hello")
        websocket.close()
        # Server-side cleanup should handle this
```

## Testing error scenarios

```python
def test_websocket_invalid():
    with pytest.raises(Exception):
        with client.websocket_connect("/ws") as websocket:
            websocket.send_text("invalid")
            websocket.receive_text()  # May raise WebSocketDisconnect
```

## WebSocket with auth

```python
def test_websocket_auth():
    with client.websocket_connect("/ws", headers={"Authorization": "Bearer token"}) as ws:
        ws.send_text("auth check")
        assert ws.receive_text() == "authenticated"
```

See [websockets-intro.md](./websockets-intro.md) for WebSocket endpoint setup.
