FROM python:3.14-slim AS builder

WORKDIR /build

COPY api/requirements.txt .
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv pip install --target=/deps -r requirements.txt

FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /deps/ /usr/local/lib/python3.14/site-packages/
COPY --from=builder /deps/bin/ /usr/local/bin/

WORKDIR /app
