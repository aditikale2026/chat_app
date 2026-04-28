from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    SECRET_KEY: str
    GROQ_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"

    # ── NEW: filesystem paths with sensible defaults ──────────
    CHROMA_PERSIST_DIR: str = "./app/Storage"
    UPLOAD_FOLDER: str = "./data"
    # ---------------------------------------------------------

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()