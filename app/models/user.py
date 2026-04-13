from sqlalchemy import Column, String, Integer
from app.db.postgressconnection import Base
from pydantic import BaseModel

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"