---
title: "Streaming — FileResponse"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - streaming
  - files
sources:
  - url: "https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse"
    title: "FastAPI Docs — FileResponse"
last_audit_date: 2026-06-09
---

# Streaming — FileResponse

Serve files efficiently with `FileResponse`:

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/download/{filename}")
async def download_file(filename: str):
    return FileResponse(
        path=f"files/{filename}",
        media_type="application/octet-stream",
        filename=filename,
    )
```

## Parameters

| Parameter | Type | Purpose |
|---|---|---|
| `path` | str | File path on disk |
| `media_type` | str | Content-Type header |
| `filename` | str | Override Content-Disposition filename |
| `headers` | dict | Additional response headers |

## File download with disposition

```python
@app.get("/export")
async def export_csv():
    return FileResponse(
        path="/tmp/report.csv",
        media_type="text/csv",
        filename="report-2026-06.csv",
        headers={
            "X-Generated-At": "2026-06-09T12:00:00Z",
            "Cache-Control": "no-cache",
        },
    )
```

## Performance notes

- `FileResponse` streams the file in chunks
- Uses `os.path.getsize()` for `Content-Length` header
- Supports range requests (partial content)
- Efficient for large files (no full-load into memory)

See [streaming-response.md](./streaming-response.md) for `StreamingResponse` and [file-response.md](./file-response.md) for custom headers with `FileResponse`.
