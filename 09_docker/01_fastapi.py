from fastapi import FastAPI

app = FastAPI(title="Hello application")

@app.get("/")
def home():
    return {"message": "Hello, world!"}


"""
uv venv
uv init --no-workspace --bare
uv add fastapi fastapi-cli
uv run fastapi 01_fastapi.py --host 0.0.0.0
"""