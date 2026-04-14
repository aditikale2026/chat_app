import os
import uuid
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends

from app.utils.uploading_system import save_uploaded_file, UPLOAD_FOLDER
from app.utils.doc_cache import store_doc
from app.utils.document_process.universal_loader import load_document
from app.utils.document_process.chunking import splitting
from app.models.schemas import UploadResponse
from app.api.v1.endpoints.auth import get_current_user
from app.db.redis_client import get_redis
from app.models.user import UserORM

router = APIRouter(prefix="/rag")


@router.post("/upload_document", response_model=UploadResponse)
async def upload_document(
    request:      Request,
    file:         UploadFile = File(...),
    current_user: UserORM    = Depends(get_current_user),
    redis=Depends(get_redis)
):
    try:
        # 1. Save to disk — validates extension
        filename = save_uploaded_file(file)

        doc_id      = str(uuid.uuid4())
        upload_time = datetime.now().isoformat()
        user_id     = current_user.username

        # 2. Enforce 3-file limit — raises ValueError if over limit
        await store_doc(redis, user_id, doc_id, filename, upload_time)

        # 3. Load with the universal loader (pdf, txt, docx, csv, md)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        documents = load_document(file_path)
        total_len = len(documents)

        # 4. Chunk and embed
        chunks = splitting(documents).split_documents()
        request.app.state.vectorstore.add_documents(
            chunks, doc_id, filename, upload_time, total_len
        )

        return {
            "answer":       f"{filename} uploaded successfully",
            "filename":     filename,
            "upload_time":  upload_time,
            "total_length": total_len
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))