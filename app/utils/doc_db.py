import os
from datetime import datetime, timezone
from typing import List, Dict, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentORM

MAX_ACTIVE_DOCS = 3

async def count_active_docs(db: AsyncSession, user_id: str) -> int:
    result = await db.execute(
        select(DocumentORM).where(DocumentORM.user_id == user_id, DocumentORM.active == True)
    )
    return len(result.scalars().all())

async def add_doc(
    db: AsyncSession,
    user_id: str,
    doc_id: str,
    filename: str,
    file_path: str,
    upload_time: datetime,
    size: Optional[int] = None,
) -> DocumentORM:
    document = DocumentORM(
        doc_id=doc_id,
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        upload_time=upload_time,
        size=size,
        active=True,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document

async def get_user_docs(db: AsyncSession, user_id: str, active_only: bool = True) -> List[Dict]:
    query = select(DocumentORM).where(DocumentORM.user_id == user_id)
    if active_only:
        query = query.where(DocumentORM.active == True)
    query = query.order_by(DocumentORM.upload_time.desc())

    result = await db.execute(query)
    documents = result.scalars().all()
    return [
        {
            "doc_id": doc.doc_id,
            "filename": doc.filename,
            "upload_time": doc.upload_time.isoformat(),
            "size": doc.size,
            "active": doc.active,
        }
        for doc in documents
    ]

async def delete_doc(db: AsyncSession, user_id: str, doc_id: str, vectorstore=None) -> None:
    result = await db.execute(
        select(DocumentORM).where(
            DocumentORM.user_id == user_id,
            DocumentORM.doc_id == doc_id,
            DocumentORM.active == True,
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise ValueError("Document not found")

    # 1. Delete from vector store if provided
    if vectorstore:
        vectorstore.delete_document_by_id(doc_id)

    # 2. Delete local file
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except OSError as e:
            print(f"Warning: Failed to delete file {document.file_path}: {e}")

    # 3. Mark as inactive in database
    await db.execute(
        update(DocumentORM)
        .where(DocumentORM.id == document.id)
        .values(active=False, deleted_at=datetime.now(timezone.utc))
    )
    await db.commit()
