---
title: "Logging Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - logging
sources:
  - url: "https://fastapi.tiangolo.com/"
    title: "FastAPI Documentation"
last_audit_date: 2026-06-09
---

# Logging Configuration

Configure logging for FastAPI applications:

```python
import logging
import sys
from fastapi import FastAPI

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log"),
    ],
)

logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/items")
async def list_items():
    logger.info("Listing all items")
    return [{"name": "Foo"}]
```

## Structured JSON logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()
```

## Uvicorn log integration

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        log_config=None,  # Use our logging config
    )
```

## Request logging via middleware

For per-request logging, see [middleware-timing.md](./middleware-timing.md).
