from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

from app.db.postgressconnection import get_db
from app.db.redis_client import get_redis          # ← new import
from app.models.user import UserORM, UserCreate
from app.config import settings

router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def make_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)          # ← inject Redis
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ── Step 1: Check blacklist FIRST ──────────────────────────
    # If the token was blacklisted (user logged out), reject immediately
    is_blacklisted = await redis.get(f"blacklist:{token}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ── Step 2: Normal JWT validation ─────────────────────────
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(UserORM).where(UserORM.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


# ── Public Endpoints ──────────────────────────────────────────

@router.post("/register")
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserORM).where(UserORM.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username taken")

    new_user = UserORM(
        username=payload.username,
        hashed_password=pwd_context.hash(payload.password),
        role=payload.role
    )
    db.add(new_user)
    await db.commit()

    token = make_token(payload.username, payload.role)
    return {
        "message": "User created",
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserORM).where(UserORM.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": make_token(user.username, user.role),
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    redis = Depends(get_redis)
):
    try:
        # Decode without verifying expiry so we can still blacklist an
        # almost-expired token correctly
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False}   # we only need the exp value
        )
        exp = payload.get("exp")

        if exp:
            # TTL = how many seconds remain until the token naturally expires
            # We store the blacklist entry for exactly that long so Redis
            # auto-deletes it once the token would have expired anyway
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = exp - now
            if ttl > 0:
                await redis.setex(f"blacklist:{token}", ttl, "1")
            # If TTL <= 0 the token is already expired — no need to store it

    except JWTError:
        # If token is malformed there's nothing to blacklist
        pass

    return {"message": "Successfully logged out"}
