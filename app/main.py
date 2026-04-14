from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import time

from app.api.v1.endpoints.query  import router as rag_query
from app.api.v1.endpoints.upload import router as rag_upload
from app.api.v1.endpoints.auth   import router as auth_router
from app.db.postgressconnection  import engine, Base
from app.db.redis_client         import init_redis, close_redis
from app.models.user             import UserORM
from app.services.vector_store   import Storing
from app.services.retrieval      import RAGRetriver
from app.langgraph_pipeline.dependencies  import set_service
from app.langgraph_pipeline.graph_builder import compile_graph
from langgraph.checkpoint.redis.aio       import AsyncRedisSaver
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Postgres
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Redis
    await init_redis()

    # 3. LangGraph — AsyncRedisSaver must stay open for app lifetime
    checkpointer = AsyncRedisSaver.from_conn_string(settings.REDIS_URL)
    await checkpointer.__aenter__()
    await checkpointer.asetup()
    app.state.graph       = compile_graph(checkpointer)
    app.state.checkpointer = checkpointer
    print("LangGraph compiled with Redis checkpointer")

    # 4. Vector store + retriever
    app.state.vectorstore = Storing()
    app.state.retriever   = RAGRetriver(vector_store=app.state.vectorstore)
    set_service("vectorstore", app.state.vectorstore)
    set_service("retriever",   app.state.retriever)

    print("App started")
    yield

    # Cleanup
    await app.state.checkpointer.__aexit__(None, None, None)
    await close_redis()
    print("App ended")


rag_api = FastAPI(title="Chatbot", lifespan=lifespan)


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