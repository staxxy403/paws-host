FROM python:3.12-slim AS builder

WORKDIR /build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv pip install --target=/deps -r requirements.txt

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /deps/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

ENTRYPOINT ["/usr/local/bin/python"]
   