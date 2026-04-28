from sqlalchemy import Column, String, Integer, DateTime, Boolean
from app.db.postgressconnection import Base

class DocumentORM(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    doc_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    upload_time = Column(DateTime(timezone=True), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    size = Column(Integer, nullable=True)
