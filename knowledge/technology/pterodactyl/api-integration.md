---
sources:
  - "https://dashflo.net/docs/api/pterodactyl/v1/"
  - "https://github.com/pterodactyl/panel"
last_audit_date: 2026-07-29
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
status: draft
date: 2026-07-29
---

# Pterodactyl API Integration

## Client API vs Application API

Pterodactyl exposes two distinct REST APIs with different scopes and authentication requirements.

| API | Base Path | Audience | API Key Prefix |
|-----|-----------|----------|----------------|
| **Client API** | `/api/client` | End-users managing their own servers | `ptlc_` |
| **Application API** | `/api/application` | Administrators managing the panel | `ptla_` |

### Authentication

Both APIs use **Bearer Token** authentication. Include the API key in the `Authorization` header:

```
Authorization: Bearer <your_api_key>
```

Every request **must** also include the following header:

```
Accept: Application/vnd.pterodactyl.v1+json
```

Omitting the `Accept` header will result in a `406 Not Acceptable` error.

---

## Key Endpoints

### Client API (`/api/client`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/client` | List all servers the user has access to |
| `GET` | `/api/client/servers/{server}` | Get server details (resources/usage) |
| `POST` | `/api/client/servers/{server}/command` | Send a console command |
| `POST` | `/api/client/servers/{server}/power` | Send a power action (`start`, `stop`, `restart`, `kill`) |
| `GET` | `/api/client/servers/{server}/websocket` | Get WebSocket credentials (JWT + URL) |
| `GET` | `/api/client/servers/{server}/resources` | Get live resource usage (CPU, RAM, disk) |
| `GET/POST/DELETE` | `/api/client/servers/{server}/files/*` | File management (list, read, write, rename, delete, compress, download) |
| `GET/POST/DELETE` | `/api/client/servers/{server}/databases/*` | Manage databases |
| `GET/POST/DELETE` | `/api/client/servers/{server}/schedules/*` | Manage schedules and tasks |
| `GET/POST/DELETE` | `/api/client/servers/{server}/backups` | Manage backups |
| `GET/POST/DELETE` | `/api/client/servers/{server}/network/allocations` | Manage network allocations |
| `GET/POST/DELETE` | `/api/client/servers/{server}/users/*` | Subuser management |

### Application API (`/api/application`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/api/application/users` | List or create users |
| `GET/PATCH/DELETE` | `/api/application/users/{id}` | Get, update, or delete a user |
| `GET/POST` | `/api/application/servers` | List or create servers |
| `GET/PATCH/DELETE` | `/api/application/servers/{id}` | Get, update, or delete a server |
| `GET/POST` | `/api/application/nodes` | List or create nodes |
| `GET/PATCH/DELETE` | `/api/application/nodes/{id}` | Get, update, or delete a node |
| `GET/POST/DELETE` | `/api/application/nodes/{id}/allocations` | Manage allocations |
| `GET/POST/DELETE` | `/api/application/locations` | Manage locations |
| `GET` | `/api/application/nests` | List all nests |
| `GET` | `/api/application/nests/{nest}/eggs` | List eggs in a nest |
| `GET` | `/api/application/nests/{nest}/eggs/{egg}` | Get egg details |

---

## Console via WebSocket

The Client API provides real-time console access over WebSocket.

### Flow

1. **Request a WebSocket token**:
   ```
   GET /api/client/servers/{server}/websocket
   ```
   Response contains a `token` (JWT) and a `socket` URL.

2. **Connect** to the returned WebSocket endpoint:
   ```
   wss://{node}:8080
   ```

3. **Authenticate** by sending the JWT token:
   ```json
   {
     "event": "auth",
     "args": ["<jwt_token>"]
   }
   ```

### Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `auth` | Client → Server | Authenticate with the JWT token |
| `send command` | Client → Server | Execute a console command |
| `send logs` | Client → Server | Request recent log lines |
| `console output` | Server → Client | Live console output |
| `status` | Server → Client | Server power state changes |
| `stats` | Server → Client | Resource usage data (CPU, memory, disk, uptime) |
| `token expiring` | Server → Client | Token is about to expire; re-auth needed |
| `daemon error` | Server → Client | Wings daemon error message |
| `install output` | Server → Client | Installation progress output |

---

## Rate Limiting

Pterodactyl enforces rate limits on a **per-API-key** basis.

| API | Limit |
|-----|-------|
| Client API | ~240 requests per minute |
| Application API | ~256 requests per minute |

Exceeding the limit returns a `429 Too Many Requests` response. Rate limits are configurable via `.env` variables (`APP_API_CLIENT_RATELIMIT`, `APP_API_APPLICATION_RATELIMIT`).

---

## Response Format

All API responses follow the [JSON:API](https://jsonapi.org/) specification.

### Successful Response

```json
{
  "data": [
    {
      "attributes": {
        "id": 1,
        "name": "My Server",
        "uuid": "abc123-def456",
        "node": 1
      }
    }
  ],
  "meta": {
    "pagination": {
      "total": 50,
      "count": 25,
      "per_page": 25,
      "current_page": 1,
      "total_pages": 2
    }
  }
}
```

---

## Example: Create a Server (Application API)

**Request:**

```http
POST /api/application/servers
Authorization: Bearer ptla_xxxxxxxxxxxxxxxxx
Accept: Application/vnd.pterodactyl.v1+json
Content-Type: application/json

{
  "name": "My Minecraft Server",
  "user": 1,
  "egg": 5,
  "docker_image": "ghcr.io/pterodactyl/yolks:java_17",
  "startup": "java -Xms128M -Xmx{{SERVER_MEMORY}}M -jar server.jar",
  "environment": {
    "SERVER_JARFILE": "server.jar",
    "VERSION": "latest"
  },
  "limits": {
    "memory": 2048,
    "swap": 0,
    "disk": 10240,
    "io": 500,
    "cpu": 200
  },
  "feature_limits": {
    "databases": 2,
    "allocations": 1,
    "backups": 3
  }
}
```

---

## Best Practices

- **Cache API responses** where possible to stay within rate limits.
- **Use the Client API** for end-user actions and the **Application API** for administrative tasks.
- **Rotate API keys** periodically and use separate keys for separate services.
- **Handle pagination** by iterating through all pages when collecting full datasets.
- **Reconnect WebSockets** gracefully on disconnect by requesting a new token and re-authenticating.
