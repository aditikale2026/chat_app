from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import time

from app.api.v1.endpoints.query  import router as rag_query
from app.api.v1.endpoints.upload import router as rag_upload
from app.api.v1.endpoints.auth   import router as auth_router
from app.db.postgressconnection  import engine, Base
from app.db.redis_client         import init_redis, close_redis, get_redis  # ← get_redis not redis_client
from app.models.user             import UserORM
from app.models.document         import DocumentORM  # ← Ensure table is created on startup
from app.services.vector_store   import Storing
from app.services.retrieval      import RAGRetriver
from app.langgraph_pipeline.dependencies       import set_service
from app.langgraph_pipeline.graph_builder      import compile_graph
from app.langgraph_pipeline.redis_checkpointer import RedisCheckpointer
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints.frontend_router import router as pages_router
# from app.frontend_router  import router as ui_proxy_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Postgres
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Redis — must happen BEFORE anything uses it
    await init_redis()

    # 3. LangGraph — call get_redis() AFTER init so it's not None
    redis = await get_redis()                        # ← fetch the live client
    checkpointer    = RedisCheckpointer(redis)       # ← now it's not None
    app.state.graph = compile_graph(checkpointer)
    print("LangGraph compiled with plain Redis checkpointer")

    # 4. Vector store + retriever
    app.state.vectorstore = Storing()
    app.state.retriever   = RAGRetriver(vector_store=app.state.vectorstore)
    set_service("vectorstore", app.state.vectorstore)
    set_service("retriever",   app.state.retriever)

    print("App started")
    yield

    await close_redis()
    print("App ended")


rag_api = FastAPI(title="Chatbot", lifespan=lifespan)
# rag_api.mount("/static", StaticFiles(directory="app/static"), name="static")

@rag_api.middleware("http")
async def log_requests(request: Request, call_next):
    start    = time.time()
    response = await call_next(request)
    print(f"{request.method} {request.url.path} → {response.status_code} "
          f"({time.time()-start:.3f}s)")
    return response


rag_api.include_router(rag_query)
rag_api.include_router(rag_upload)
rag_api.include_router(auth_router)
rag_api.include_router(pages_router)
