"""UI endpoints - Frontend integration layer
Maps frontend requests to backend services"""

from fastapi import APIRouter, HTTPException, Depends, Cookie, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from app.db.postgressconnection import get_db
from app.db.redis_client import get_redis
from app.models.user import UserORM, UserCreate
from app.config import settings

router = APIRouter(prefix="/ui")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


def make_token(username: str, role: str = "user") -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


@router.post("/login")
async def login(
    credentials: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Login user and return JWT token"""
    result = await db.execute(
        select(UserORM).where(UserORM.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(
        credentials.password, user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = make_token(credentials.username, user.role or "user")
    
    # Set token in cookie for API requests (non-HttpOnly so JS can also read)
    response.set_cookie(
        key="access_token",
        value=token,
        secure=True,
        samesite="lax",
        max_age=3600,  # 1 hour
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/register")
async def register(
    user_data: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Register new user and return JWT token"""
    result = await db.execute(
        select(UserORM).where(UserORM.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = UserORM(
        username=user_data.username,
        hashed_password=pwd_context.hash(user_data.password),
        role="user",
    )
    db.add(new_user)
    await db.commit()

    token = make_token(user_data.username, "user")
    
    # Set token in cookie for API requests (non-HttpOnly so JS can also read)
    response.set_cookie(
        key="access_token",
        value=token,
        secure=True,
        samesite="lax",
        max_age=3600,
    )

    return {
        "message": "Registration successful",
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    response: Response,
    access_token: str = Cookie(default=None),
    redis=Depends(get_redis),
):
    """Logout user by blacklisting token"""
    if not access_token:
        return {"message": "Already logged out"}

    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        exp = payload.get("exp")

        if exp:
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = exp - now
            if ttl > 0:
                await redis.setex(f"blacklist:{access_token}", ttl, "1")

    except JWTError:
        pass

    # Clear cookie
    response.delete_cookie(key="access_token")

    return {"message": "Logout successful"}
