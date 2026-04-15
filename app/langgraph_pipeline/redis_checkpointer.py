"""
Plain-Redis checkpointer for LangGraph.
No RediSearch / Redis Stack required.
"""
import json
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Tuple
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer


class RedisCheckpointer(BaseCheckpointSaver):

    serde = JsonPlusSerializer()

    def __init__(self, redis_client):
        super().__init__()
        self.redis = redis_client
        self.TTL   = 86400 * 7   # 7 days

    # ── Key helpers ──────────────────────────────────────────
    def _checkpoint_key(self, thread_id: str) -> str:
        return f"langgraph:checkpoint:{thread_id}"

    def _writes_key(self, thread_id: str) -> str:
        return f"langgraph:writes:{thread_id}"

    # ════════════════════════════════════════════════════════
    # SYNC methods (required by base class)
    # ════════════════════════════════════════════════════════

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        raise NotImplementedError("Use async version — call aget_tuple instead")

    def list(
        self,
        config:   Optional[dict],
        *,
        filter:   Optional[Dict[str, Any]] = None,
        before:   Optional[dict]           = None,
        limit:    Optional[int]            = None,
    ) -> Iterator[CheckpointTuple]:
        # Sync list not supported — return empty iterator
        return iter([])

    def put(
        self,
        config:       dict,
        checkpoint:   Checkpoint,
        metadata:     CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        raise NotImplementedError("Use async version — call aput instead")

    def put_writes(
        self,
        config:   dict,
        writes:   List[Tuple[str, Any]],
        task_id:  str,
    ) -> None:
        pass   # no-op for sync

    # ════════════════════════════════════════════════════════
    # ASYNC methods (what LangGraph actually calls)
    # ════════════════════════════════════════════════════════

    async def aget_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        try:
            thread_id = config["configurable"]["thread_id"]
            raw = await self.redis.get(self._checkpoint_key(thread_id))
            if not raw:
                return None

            data       = json.loads(raw)
            checkpoint = self.serde.loads_typed((data["type"], data["checkpoint"]))
            metadata   = data.get("metadata", {})

            return CheckpointTuple(
                config=config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=None,
                pending_writes=[]
            )
        except Exception as e:
            print(f"[RedisCheckpointer] aget_tuple error: {e}")
            return None

    async def aput(
        self,
        config:       dict,
        checkpoint:   Checkpoint,
        metadata:     CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        try:
            thread_id        = config["configurable"]["thread_id"]
            type_, serialised = self.serde.dumps_typed(checkpoint)

            data = json.dumps({
                "type":       type_,
                "checkpoint": serialised,
                "metadata":   metadata or {},
            })

            await self.redis.setex(
                self._checkpoint_key(thread_id),
                self.TTL,
                data
            )
        except Exception as e:
            print(f"[RedisCheckpointer] aput error: {e}")
        return config

    async def aput_writes(
        self,
        config:  dict,
        writes:  List[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        # pending writes not needed for basic persistence — safe no-op
        pass

    async def alist(
        self,
        config:   Optional[dict],
        *,
        filter:   Optional[Dict[str, Any]] = None,
        before:   Optional[dict]           = None,
        limit:    Optional[int]            = None,
    ) -> AsyncIterator[CheckpointTuple]:
        # Return empty async iterator
        return
        yield   # makes this an async generator