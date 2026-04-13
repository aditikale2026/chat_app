from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.db.postgressconnection import get_db
from app.models.user import UserORM, UserCreate
from app.config import settings
from pydantic import BaseModel
router = APIRouter(prefix="/auth")
pwd = CryptContext(schemes=["bcrypt"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

# add this model in auth.py
class LoginRequest(BaseModel):
    username: str
    password: str
    
    
def make_token(username: str, role: str):
    return jwt.encode(
        {"sub": username, "role": role, "exp": datetime.utcnow() + timedelta(hours=1)},
        settings.SECRET_KEY, algorithm="HS256"
    )

async def get_current_user(token: str = Depends(oauth2), db: AsyncSession = Depends(get_db)):
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        result = await db.execute(select(UserORM).where(UserORM.username == data["sub"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).where(UserORM.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username taken")
    db.add(UserORM(username=payload.username, hashed_password=pwd.hash(payload.password), role=payload.role))
    await db.commit()
    return {"message": "User created"}


@router.post("/login")
async def login(form: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).where(UserORM.username == form.username))
    user = result.scalar_one_or_none()
    if not user or not pwd.verify(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": make_token(user.username, user.role), "token_type": "bearer"}