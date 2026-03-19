from app.api.v1.endpoints.query import router as rag_query
from app.api.v1.endpoints.upload import router as rag_upload
from app.services.vector_store import Storing
from app.services.retrieval import RAGRetriver
from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
import time 

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("app started")
    app.state.vectorstore = Storing()
    app.state.retriever = RAGRetriver(vector_store=app.state.vectorstore)

    yield

    print("app ended")

rag_api=FastAPI(title="Chatbot ",lifespan=lifespan)

@rag_api.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    print(f"Incoming Request: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.time() - start_time

    print(f"Completed in {process_time:.4f} seconds")
    print("Status Code:", response.status_code)
    print("-----------------------------------")

    return response

rag_api.include_router(rag_query)
rag_api.include_router(rag_upload)