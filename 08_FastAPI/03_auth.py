import secrets
import logging
from fastapi import FastAPI, Header, HTTPException, status, Body, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel, Field

logging.getLogger('passlib').setLevel(logging.ERROR)

class UserDB(BaseModel):
    login: str
    is_admin: bool
    hashed_pw: str

class LoginRequest(BaseModel):
    login: str
    pw: str

class LoginResponse(BaseModel):
    token: str


class CreateBook(BaseModel):
    title: str
    author: str

class SuccessMessage(BaseModel):
    message: str = Field(examples=["Операция успешно выполнена"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = [
    UserDB(
        login="admin",
        is_admin=True,
        hashed_password=pwd_context.hash("adminpass"),
    ),
    UserDB(
        login="miha",
        is_admin=False,
        hashed_password=pwd_context.hash("solovev"),
    ),
]

sessions = {}

def user_from_login(login: str) -> UserDB|None:
    for user in users:
        if user.login == login:
            return user
    return None

def user_from_token(token: str) -> UserDB|None:
    user_login = sessions.get(token)
    if not user_login:
        return None
    return user_from_login(user_login)

app = FastAPI()

@app.post("auth/login")
async def auth_user(data: LoginRequest = Body()):
    user = user_from_login(data.login)
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = secrets.token_hex(32)
    sessions[token] = user.login
    return LoginResponse(token=token)

@app.post("/admin/books")
async def create_book(data: CreateBook = Body(), token: str|None = Header(None, alias="Authorization")):
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    user = user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    print(data) # saving data
    return SuccessMessage(message="Book created successfully")

@app.post("/admin/books2")
async def create_book(data: CreateBook = Body(), credentials: HTTPAuthorizationCredentials|None = Depends(HTTPBearer(auto_error=False))):
    if not credentials:
        raise HTTPException(status_code=401, detail="No token")
    token =  credentials.credentials
    user = user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    print(data) # saving data
    return SuccessMessage(message="Book created successfully")