"""
auth.py — Single source of truth for all authentication.
Supports both:
  • Authorization: Bearer <token>   (API / curl clients)
  • access_token cookie              (React SPA)

Endpoints:
  POST /auth/register
  POST /auth/login
  POST /auth/logout
  POST /auth/refresh
"""

from fastapi import APIRouter, HTTPException, Depends, status, Cookie, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import Optional

from app.db.postgressconnection import get_db
from app.db.redis_client import get_redis
from app.models.user import UserORM, UserCreate
from app.config import settings

router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tokenUrl must match the login endpoint so Swagger UI works
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

ACCESS_TOKEN_EXPIRE_HOURS  = 1
REFRESH_TOKEN_EXPIRE_HOURS = 24 * 7   # 7 days


# ── Pydantic models ───────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


# ── Token helpers ─────────────────────────────────────────────

def _make_token(username: str, role: str, kind: str = "access") -> str:
    """
    kind = "access"  → 1-hour token
    kind = "refresh" → 7-day token  (stored in Redis so it can be revoked)
    """
    if kind == "refresh":
        expire = datetime.now(timezone.utc) + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    payload = {"sub": username, "role": role, "exp": expire, "kind": kind}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Write both tokens as Secure, SameSite=Lax cookies."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,   # JS needs to read it for Authorization header
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,    # Refresh token is HttpOnly — JS can't touch it
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_HOURS * 3600,
    )


def _clear_auth_cookies(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


# ── Token extraction: Bearer header OR cookie ─────────────────

async def _extract_token(
    bearer: Optional[str] = Depends(oauth2_scheme),
    access_token: Optional[str] = Cookie(default=None),
) -> str:
    """
    Returns the raw JWT string from whichever source is available.
    Bearer header takes priority over cookie.
    Raises 401 if neither is present.
    """
    token = bearer or access_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# ── get_current_user (used by all protected endpoints) ────────

async def get_current_user(
    token: str = Depends(_extract_token),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Blacklist check (covers both Bearer and cookie tokens)
    if await redis.get(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. JWT validation
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        kind: str = payload.get("kind", "access")
        if username is None or kind != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 3. DB lookup
    result = await db.execute(select(UserORM).where(UserORM.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


# ── Helper: blacklist a token until its natural expiry ────────

async def _blacklist_token(token: str, redis):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        exp = payload.get("exp")
        if exp:
            ttl = exp - int(datetime.now(timezone.utc).timestamp())
            if ttl > 0:
                await redis.setex(f"blacklist:{token}", ttl, "1")
    except JWTError:
        pass


# ── Public endpoints ──────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserORM).where(UserORM.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = UserORM(
        username=payload.username,
        hashed_password=pwd_context.hash(payload.password),
        role="user",
    )
    db.add(new_user)
    await db.commit()

    access_token  = _make_token(payload.username, "user", "access")
    refresh_token = _make_token(payload.username, "user", "refresh")
    _set_auth_cookies(response, access_token, refresh_token)

    return {
        "message": "Registration successful",
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login")
async def login(
    credentials: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserORM).where(UserORM.username == credentials.username))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token  = _make_token(user.username, user.role or "user", "access")
    refresh_token = _make_token(user.username, user.role or "user", "refresh")
    _set_auth_cookies(response, access_token, refresh_token)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login/form")
async def login_form(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 form-based login — kept for Swagger UI compatibility."""
    result = await db.execute(select(UserORM).where(UserORM.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token  = _make_token(user.username, user.role or "user", "access")
    refresh_token = _make_token(user.username, user.role or "user", "refresh")
    _set_auth_cookies(response, access_token, refresh_token)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    response: Response,
    token: str = Depends(_extract_token),
    refresh_token: Optional[str] = Cookie(default=None),
    redis=Depends(get_redis),
):
    # Blacklist whatever token was provided (Bearer or cookie)
    await _blacklist_token(token, redis)

    # Also blacklist the refresh token if present
    if refresh_token:
        await _blacklist_token(refresh_token, redis)

    _clear_auth_cookies(response)
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_access_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    Exchange a valid refresh_token cookie for a new access_token.
    Called automatically by the frontend when it gets a 401.
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    # Check blacklist
    if await redis.get(f"blacklist:{refresh_token}"):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        kind     = payload.get("kind")
        if not username or kind != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Verify user still exists
    result = await db.execute(select(UserORM).where(UserORM.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = _make_token(user.username, user.role or "user", "access")
    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )

    return {"access_token": new_access, "token_type": "bearer"}


@router.get("/me")
async def me(current_user: UserORM = Depends(get_current_user)):
    """Return basic info about the currently authenticated user."""
    return {"username": current_user.username, "role": current_user.role}