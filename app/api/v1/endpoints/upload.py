import os
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.uploading_system import save_uploaded_file, UPLOAD_FOLDER
from app.utils.doc_db import add_doc, count_active_docs, get_user_docs, delete_doc
from app.utils.document_process.universal_loader import load_document
from app.utils.document_process.chunking import splitting
from app.models.schemas import UploadResponse
from app.api.v1.endpoints.auth import get_current_user
from app.db.postgressconnection import get_db
from app.models.user import UserORM

router = APIRouter(prefix="/rag")


# ─────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────

class UserDocumentRecord(BaseModel):
    """Model returned to frontend - only essential fields."""
    doc_id: str
    filename: str
    upload_time: str


class UserDocumentsResponse(BaseModel):
    documents: List[UserDocumentRecord]
    count: int


@router.post("/upload_document", response_model=UploadResponse)
async def upload_document(
    request:      Request,
    file:         UploadFile = File(...),
    current_user: UserORM    = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    filename = None
    try:
        # 1. Save to disk — validates extension
        filename = save_uploaded_file(file)
        doc_id = str(uuid.uuid4())
        upload_time = datetime.now(timezone.utc)
        user_id = current_user.username
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # 2. Enforce 3 active documents per user (before any heavy processing)
        active_count = await count_active_docs(db, user_id)
        if active_count >= 3:
            # Clean up the file we just saved
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            raise ValueError(
                f"Upload limit reached (3 files max). Your current files: {active_count}. "
                "Delete one before uploading another."
            )

        file_size = os.path.getsize(file_path)

        try:
            # 3. Load with the universal loader (pdf, txt, docx, csv, md)
            documents = load_document(file_path)
            if not documents:
                raise ValueError("No content could be extracted from the file")
            total_len = len(documents)

            # 4. Chunk and embed
            chunks = splitting(documents).split_documents()
            if not chunks:
                raise ValueError("File could not be processed into chunks")

            # 5. Add to vector store
            request.app.state.vectorstore.add_documents(
                chunks, doc_id, filename, upload_time.isoformat(), total_len
            )
        except Exception as doc_error:
            # If document processing fails, delete the file we saved
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            raise ValueError(f"Failed to process document: {str(doc_error)}")

        # 6. Save metadata to Postgres
        await add_doc(db, user_id, doc_id, filename, file_path, upload_time, file_size)

        return {
            "answer":       f"{filename} uploaded successfully",
            "filename":     filename,
            "upload_time":  upload_time.isoformat(),
            "total_length": total_len
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        # Generic cleanup on unexpected errors
        if filename:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@router.get("/user_documents", response_model=UserDocumentsResponse)
async def get_user_documents(
    current_user: UserORM = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
    active_only: bool = Query(True, description="Return only currently active documents"),
):
    """Get uploaded documents for the current user.

    By default this returns only active docs, but setting `active_only=false`
    will return the user's full upload history stored in Postgres.
    """
    documents = await get_user_docs(db, current_user.username, active_only=active_only)
    # Convert to frontend model: only include doc_id, filename, upload_time
    frontend_docs = [
        UserDocumentRecord(
            doc_id=doc["doc_id"],
            filename=doc["filename"],
            upload_time=doc["upload_time"]
        )
        for doc in documents
    ]
    return UserDocumentsResponse(
        documents=frontend_docs,
        count=len(frontend_docs)
    )


@router.delete("/delete_document/{doc_id}")
async def delete_document(
    doc_id: str,
    request: Request,
    current_user: UserORM = Depends(get_current_user),
    db:           AsyncSession = Depends(get_db),
):
    """Delete a document by doc_id from database and vector store."""
    try:
        # Get vectorstore from app state if available
        vectorstore = None
        if hasattr(request.app.state, 'vectorstore'):
            vectorstore = request.app.state.vectorstore
        
        await delete_doc(db, current_user.username, doc_id, vectorstore=vectorstore)
        return {"message": f"Document {doc_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))