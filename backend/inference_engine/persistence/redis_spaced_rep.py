import time

from redis.asyncio import Redis

from inference_engine.memory.spaced_repetition import (
    compute_next_review_timestamp,
    process_review_result
)

SPACED_REP_TTL = 2592000  # 30 days


class RedisSpacedRepManager:
    def __init__(self, redis: Redis) -> None:
        self._r = redis

    # ── Keys ──
    @staticmethod
    def _queue_key(child_id: str) -> str:
        return f"spaced_rep:{child_id}"

    @staticmethod
    def _meta_key(child_id: str, hito_id: str) -> str:
        return f"spaced_rep:{child_id}:{hito_id}"

    # ── Enqueue ──
    async def enqueue_hito(
        self, child_id: str, hito_id: str, stage: int = 1
    ) -> None:
        now = time.time()
        next_ts = compute_next_review_timestamp(stage, now)

        queue_key = self._queue_key(child_id)
        await self._r.zadd(queue_key, {hito_id: next_ts})
        await self._r.expire(queue_key, SPACED_REP_TTL)

        meta_key = self._meta_key(child_id, hito_id)
        await self._r.hset(meta_key, mapping={
            "stage": str(stage),
            "last_ipf": "0.0",
            "enqueued_at": str(now),
        })
        await self._r.expire(meta_key, SPACED_REP_TTL)

    # ── Query ──
    async def get_pending_reviews(
        self, child_id: str, now_ts: float | None = None
    ) -> list[dict]:
        if now_ts is None:
            now_ts = time.time()

        queue_key = self._queue_key(child_id)
        members = await self._r.zrangebyscore(
            queue_key, "-inf", now_ts, withscores=True
        )

        results = []
        for hito_id_raw, score in members:
            hito_id = (
                hito_id_raw.decode()
                if isinstance(hito_id_raw, bytes) else hito_id_raw
            )
            meta = await self._r.hgetall(
                self._meta_key(child_id, hito_id)
            )
            stage = int(meta.get(b"stage", meta.get("stage", 1)))
            results.append({
                "hito_id": hito_id,
                "next_review_ts": score,
                "stage": stage,
            })

        results.sort(key=lambda r: r["next_review_ts"])
        return results

    # ── Advance ──
    async def advance_stage(
        self, child_id: str, hito_id: str, ipf: float
    ) -> bool:
        meta_key = self._meta_key(child_id, hito_id)
        meta = await self._r.hgetall(meta_key)
        if not meta:
            return False

        current_stage = int(meta.get(b"stage", meta.get("stage", 1)))
        new_stage, graduated = process_review_result(current_stage, ipf)

        if graduated:
            await self.graduate_hito(child_id, hito_id)
            return True

        now = time.time()
        next_ts = compute_next_review_timestamp(new_stage, now)

        await self._r.zadd(self._queue_key(child_id), {hito_id: next_ts})
        await self._r.hset(meta_key, mapping={
            "stage": str(new_stage),
            "last_ipf": str(ipf),
        })
        return False

    # ── Graduate ──
    async def graduate_hito(
        self, child_id: str, hito_id: str
    ) -> None:
        await self._r.zrem(self._queue_key(child_id), hito_id)
        await self._r.delete(self._meta_key(child_id, hito_id))

    # ── Stats ──
    async def get_queue_stats(self, child_id: str) -> dict:
        queue_key = self._queue_key(child_id)
        total = await self._r.zcard(queue_key)
        now = time.time()
        due_now = await self._r.zcount(queue_key, "-inf", now)
        return {
            "total": total,
            "due_now": due_now,
        }
