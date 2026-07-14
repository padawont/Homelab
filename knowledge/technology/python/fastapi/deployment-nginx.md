---
title: "Deployment — Nginx Reverse Proxy"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - deployment
  - nginx
sources:
  - url: "https://fastapi.tiangolo.com/deployment/"
    title: "FastAPI Docs — Deployment"
last_audit_date: 2026-06-09
---

# Deployment — Nginx Reverse Proxy

Configure Nginx as a reverse proxy in front of FastAPI:

```nginx
# /etc/nginx/sites-available/fastapi
upstream app {
    server 127.0.0.1:8000;
    # Add more servers for load balancing
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Increase body size for file uploads
    client_max_body_size 100M;
}
```

## SSL termination

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;

    location / {
        proxy_pass http://app;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

## SSE/streaming support

```nginx
location /events {
    proxy_pass http://app;
    proxy_buffering off;          # Critical for SSE
    proxy_cache off;
    proxy_set_header Connection '';
    chunked_transfer_encoding on;
}
```

## Static files

For serving static files directly via Nginx (more efficient):

```nginx
location /static/ {
    alias /var/www/app/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

See [deployment-docker.md](./deployment-docker.md) for containerized deployment and [streaming-sse.md](./streaming-sse.md) for SSE headers.
