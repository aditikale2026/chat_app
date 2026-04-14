from sqlalchemy import Column, String, Integer, DateTime
from app.db.postgressconnection import Base
from pydantic import BaseModel

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    refresh_token = Column(String, nullable=True)           # add
    refresh_token_expiry = Column(DateTime(timezone=True), nullable=True)  # add

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"