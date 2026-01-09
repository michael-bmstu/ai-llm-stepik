FROM python:3.12-slim

WORKDIR ./app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY init_db.py spams.csv ./
COPY schema.py spam_api.py ./

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "spam_api.py"]


# cd 10_DataBase/05_qdrant
# uv venv
# uv init --no-workspace --bare
# uv add -r requirements.txt