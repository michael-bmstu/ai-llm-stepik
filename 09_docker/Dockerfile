FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock .

RUN uv sync

COPY 01_fastapi.py .

EXPOSE 8000

ENTRYPOINT ["uv", "run", "fastapi", "run", "01_fastapi.py", "--host", "0.0.0.0", "--port", "8000"]