---
title: "FileResponse — Headers and Media Type"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - files
sources:
  - url: "https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse"
    title: "FastAPI Docs — FileResponse"
last_audit_date: 2026-06-09
---

# FileResponse — Headers and Media Type

Full `FileResponse` configuration:

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/media/{file_id}")
async def get_media(file_id: str):
    file_path = f"/data/media/{file_id}.mp4"

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=f"video-{file_id}.mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=31536000, immutable",
            "X-Content-Type-Options": "nosniff",
        },
    )
```

## Conditional responses

`FileResponse` automatically handles:
- `Content-Length` — set from file size
- `Content-Type` — inferred from `media_type` parameter
- `Content-Disposition` — set from `filename` for downloads
- Range requests — `206 Partial Content` if range header present

## Security considerations

```python
import os
from fastapi import HTTPException, status

@app.get("/download/{filename}")
async def safe_download(filename: str):
    # Prevent path traversal
    safe_path = os.path.normpath(f"/safe/dir/{filename}")
    if not safe_path.startswith("/safe/dir/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if not os.path.exists(safe_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return FileResponse(path=safe_path)
```

See [streaming-file.md](./streaming-file.md) for basic FileResponse usage and [static-files.md](./static-files.md) for serving directories.
