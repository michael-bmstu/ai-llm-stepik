FROM python:3.12-slim

WORKDIR /app

RUN install uv

COPY pyproject.toml uv.lock .

RUN uv sync

COPY 01_fastapi.py .

EXPOSE 8000

ENTRYPOiNT ["uv", "run", "fastapi", "app.py", "--host", "0.0.0.0", "--port", "8000"]