# syntax=docker/dockerfile:1

# cv sender worker — Playwright-driven erhvervspraktik outreach (ADR-612, epic #611).
# The Playwright Python image ships headless Chromium plus its system dependencies,
# so no `playwright install` step is needed.
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Python dependencies first, so application edits do not bust the pip layer.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application source (includes src/templates/).
# Only code is copied — never the CV, .env, data/, or any credential.
COPY src/ ./src/

# Runtime mount points, populated at container start and never baked in:
#   /app/data       -> PVC  (state.db, run artefacts)
#   /app/config/cv  -> CV PDF + non-secret config (ConfigMap)
# Secrets (e.g. the Gmail App Password) are injected via k8s Secret / --env-file.
RUN mkdir -p /app/data /app/config/cv

ENTRYPOINT ["python", "-m", "src.main", "worker"]
