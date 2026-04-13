import os
import traceback
import uuid
from pydantic import BaseModel,Field
from datetime import datetime
from langgraph.checkpoint.memory import InMemorySaver

from app.langgraph_pipeline.graph_builder import graph
from fastapi import APIRouter, UploadFile, File, HTTPException, Form ,Request,Depends
 

# from app.services.vector_store import Storing
# from app.services.retrieval import RAGRetriver
from app.utils.uploading_system import save_uploaded_file,UPLOAD_FOLDER
from app.utils.doc_cache import get_doc_id,store_doc_id
from app.utils.document_process.pdf_loader import PDFProcessor
from app.utils.document_process.chunking import splitting
from app.models.schemas import UploadResponse
from app.api.v1.endpoints.auth import get_current_user   
from app.models.user import UserORM                       

# vectorstore=Storing()
# retriever = RAGRetriver(vector_store=vectorstore)
memory=InMemorySaver()
router=APIRouter(prefix="/rag")

@router.post("/upload_document",response_model=UploadResponse)
async def upload_document(request:Request,file: UploadFile = File(...),current_user: UserORM = Depends(get_current_user)):
    try:

        filename = save_uploaded_file(file)

        doc_id = str(uuid.uuid4())
        upload_time = datetime.now().isoformat()
        user_id = "abc"
        access_level=1
        # filename_id = filename+doc_id
        store_doc_id(doc_id)
        print(f"doc_id = {doc_id}")
        print(f"upload_time = {upload_time}")
        print(f"user_id = {user_id}")
        print(f"access_level = {access_level}")
        # print(f"filename_id = {filename_id}")
         
        

        file_path=os.path.join(UPLOAD_FOLDER,filename)
        loader = PDFProcessor(file_path)
        documents = loader.process_pdfs()
        
        total_len=len(documents)
        
        splitter = splitting(documents)
        chunks = splitter.split_documents()
        request.app.state.vectorstore.add_documents(chunks,doc_id,filename,upload_time,total_len)
        return {
            "answer":f"{filename} has been uploaded",
            "filename":filename,
            "upload_time":upload_time,
            "total_length":total_len
                         }
     
             
    except ValueError as e:
        print(e)
    
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
        traceback() 