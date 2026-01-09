FROM python:3.12-slim

WORKDIR ./app

RUN pip install uv

COPY procject.toml uv.lock .

RUN uv sync

COPY init_db.py .
RUN uv run python init_db.py

COPY schema.py spam_api.py .

EXPOSE 8000

ENTRYPOINT ["fastapi", "run", "spam_api.py",]


# cd 10_DataBase/05_qdrant
# uv venv
# uv init --no-workspace --bare
# uv add fastapi fastapi-cli
# uv run fastapi 01_fastapi.py --host 0.0.0.0