from app.api.v1.endpoints.query import router as rag_query
from app.api.v1.endpoints.upload import router as rag_upload
from app.api.v1.endpoints.auth import router as auth_router        
from app.db.postgressconnection import engine, Base               
from app.models.user import UserORM                               
from app.services.vector_store import Storing
from app.services.retrieval import RAGRetriver
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from app.langgraph_pipeline.dependencies import set_service
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create postgres tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("app started")
    app.state.vectorstore = Storing()
    app.state.retriever = RAGRetriver(vector_store=app.state.vectorstore)
    set_service("vectorstore", app.state.vectorstore)
    set_service("retriever", app.state.retriever)

    yield
    print("app ended")

rag_api = FastAPI(title="Chatbot", lifespan=lifespan)

@rag_api.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"Incoming Request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Completed in {process_time:.4f} seconds")
    return response

rag_api.include_router(rag_query)
rag_api.include_router(rag_upload)
rag_api.include_router(auth_router)   