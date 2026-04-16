import hashlib
import json
import traceback
from fastapi import APIRouter, Request, HTTPException, Depends
from app.models.schemas import RAGRequest, RAGResponse
from app.api.v1.endpoints.auth import get_current_user
from app.db.redis_client import get_redis
from app.models.user import UserORM

router = APIRouter(prefix="/rag")

RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW   = 60
ANSWER_CACHE_TTL    = 60 * 60


async def enforce_rate_limit(redis, username: str):
    key   = f"ratelimit:{username}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, RATE_LIMIT_WINDOW)
    if count > RATE_LIMIT_REQUESTS:
        ttl = await redis.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {ttl}s."
        )


def make_cache_key(query: str) -> str:
    normalised = query.strip().lower()
    return "answer_cache:" + hashlib.md5(normalised.encode()).hexdigest()


@router.post("/query", response_model=RAGResponse)
async def rag_query_endpoint(
    request:      RAGRequest,
    req:          Request,
    current_user: UserORM = Depends(get_current_user),
    redis=Depends(get_redis)
):
    try:
        # Get username directly from token (avoid DB lazy-load)
        username = current_user.username if hasattr(current_user, 'username') else str(current_user)
        
        # 1. Rate limit
        await enforce_rate_limit(redis, username)

        # 2. Cache check
        cache_key  = make_cache_key(request.query)
        cached_raw = await redis.get(cache_key)
        if cached_raw:
            cached = json.loads(cached_raw)
            return {"query": cached["query"], "answer": cached["answer"], "mode": cached["mode"]}

        print(f"[query] Cache MISS '{request.query}' — running pipeline")

        # 3. Check graph is available
        if not hasattr(req.app.state, "graph") or req.app.state.graph is None:
            raise HTTPException(status_code=500, detail="Graph not initialised on app state")

        graph = req.app.state.graph

        config = {"configurable": {"thread_id": username}}

        initial_state = {"query": request.query, "answer": ""}

        final_state = await graph.ainvoke(initial_state, config=config)

        answer = final_state.get("answer", "")
        if not answer or answer.strip() == "":
            raise HTTPException(
                status_code=404,
                detail="No answer found in the provided documents."
            )

        result = {
            "query":  final_state["query"],
            "answer": answer,
            "mode":   final_state.get("mode", "unknown")
        }

        await redis.setex(cache_key, ANSWER_CACHE_TTL, json.dumps(result))
        return result

    except HTTPException:
        raise

    except Exception as e:
        # Print the FULL traceback to your terminal so you can see exactly what broke
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e) or repr(e))