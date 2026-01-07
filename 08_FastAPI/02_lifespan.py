from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App startup")
    yield
    print("App sutdown")

app = FastAPI(lifespan=lifespan)