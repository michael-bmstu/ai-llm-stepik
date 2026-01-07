from fastapi import FastAPI

app = FastAPI(title="Hello application")

@app.get("/")
def home():
    return {"message": "Hello, world!"}


"""set venv
uv venv
uv init --no-workspace --bare
uv add fastapi fastapi-cli
uv run fastapi 01_fastapi.py --host 0.0.0.0
"""

"""docker
docker build -t fastapi-uv .
docker run -p 8000:8000 fastapi-uv
"""