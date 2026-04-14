import hashlib
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from app.models.schemas import RAGRequest, RAGResponse
from app.api.v1.endpoints.auth import get_current_user
from app.db.redis_client import get_redis
from app.models.user import UserORM

router = APIRouter(prefix="/rag")

RATE_LIMIT_REQUESTS = 20        # max requests per user
RATE_LIMIT_WINDOW   = 60        # per 60 seconds
ANSWER_CACHE_TTL    = 60 * 60   # cache answers for 1 hour


async def enforce_rate_limit(redis, username: str):
    key   = f"ratelimit:{username}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, RATE_LIMIT_WINDOW)
    if count > RATE_LIMIT_REQUESTS:
        ttl = await redis.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {ttl}s "
                   f"({RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s)."
        )


def make_cache_key(query: str) -> str:
    """Normalise query then hash it — same question from any user hits same key."""
    normalised = query.strip().lower()
    return "answer_cache:" + hashlib.md5(normalised.encode()).hexdigest()


@router.post("/query", response_model=RAGResponse)
async def rag_query_endpoint(
    request:      RAGRequest,
    req:          Request,
    current_user: UserORM = Depends(get_current_user),
    redis=Depends(get_redis)
):
    # ── 1. Rate limit ────────────────────────────────────────
    await enforce_rate_limit(redis, current_user.username)

    # ── 2. Global answer cache ───────────────────────────────
    cache_key  = make_cache_key(request.query)
    cached_raw = await redis.get(cache_key)
    if cached_raw:
        cached = json.loads(cached_raw)
        print(f"[query] Cache HIT  '{request.query}'")
        return {"query": cached["query"], "answer": cached["answer"], "mode": cached["mode"]}

    print(f"[query] Cache MISS '{request.query}' — running pipeline")

    # ── 3. Run LangGraph pipeline ────────────────────────────
    try:
        graph = req.app.state.graph

        config = {"configurable": {"thread_id": current_user.username}}

        final_state = graph.invoke(
            {"query": request.query, "answer": ""},
            config=config
        )

        if not final_state.get("answer") or final_state["answer"].strip() == "":
            raise HTTPException(
                status_code=404,
                detail="No answer found in the provided documents."
            )

        result = {
            "query":  final_state["query"],
            "answer": final_state["answer"],
            "mode":   final_state["mode"]
        }

        # ── 4. Store in cache for future users ───────────────
        await redis.setex(cache_key, ANSWER_CACHE_TTL, json.dumps(result))

        return result

    except (ValueError, HTTPException):
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))