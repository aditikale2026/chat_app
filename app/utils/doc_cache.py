"""
Redis-backed document tracker.
Completely replaces the old in-process global list.

Per-user structure stored in Redis:
  key  : user_docs:{username}
  value: JSON list of {doc_id, filename, upload_time}
  TTL  : 7 days (refreshed on every upload)
"""
import json
from typing import List, Dict

MAX_DOCS_PER_USER = 3
DOC_TTL           = 86400 * 7   # 7 days


def _key(user_id: str) -> str:
    return f"user_docs:{user_id}"


async def store_doc(redis, user_id: str, doc_id: str,
                    filename: str, upload_time: str) -> None:
    """
    Register a new document for this user.
    Raises ValueError if the user already has MAX_DOCS_PER_USER docs.
    """
    raw  = await redis.get(_key(user_id))
    docs: List[Dict] = json.loads(raw) if raw else []

    if len(docs) >= MAX_DOCS_PER_USER:
        names = ", ".join(d["filename"] for d in docs)
        raise ValueError(
            f"Upload limit reached ({MAX_DOCS_PER_USER} files max). "
            f"Your current files: {names}. "
            f"Delete one before uploading another."
        )

    docs.append({"doc_id": doc_id, "filename": filename, "upload_time": upload_time})
    await redis.setex(_key(user_id), DOC_TTL, json.dumps(docs))
    print(f"[doc_cache] {user_id} now has {len(docs)} doc(s)")


async def get_user_docs(redis, user_id: str) -> List[Dict]:
    """All document records for this user."""
    raw = await redis.get(_key(user_id))
    return json.loads(raw) if raw else []


async def remove_doc(redis, user_id: str, doc_id: str) -> None:
    """Remove one document from the user's list (call when user deletes a file)."""
    raw  = await redis.get(_key(user_id))
    docs = json.loads(raw) if raw else []
    docs = [d for d in docs if d["doc_id"] != doc_id]
    await redis.setex(_key(user_id), DOC_TTL, json.dumps(docs))
    print(f"[doc_cache] removed doc_id={doc_id} for {user_id}")


async def get_active_doc_ids(redis, user_id: str) -> List[str]:
    """Just the doc_id strings — used by the retriever."""
    return [d["doc_id"] for d in await get_user_docs(redis, user_id)]