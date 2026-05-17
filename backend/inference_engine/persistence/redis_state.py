import json
from dataclasses import asdict

from redis.asyncio import Redis

from inference_engine.schemas import BKTState, SessionContext

SESSION_TTL = 86400  # 24 hours


class RedisStateManager:
    def __init__(self, redis: Redis) -> None:
        self._r = redis

    # ── Keys ──
    @staticmethod
    def _state_key(child_id: str) -> str:
        return f"session:{child_id}:state"

    @staticmethod
    def _context_key(child_id: str) -> str:
        return f"session:{child_id}:context"

    @staticmethod
    def _history_key(child_id: str) -> str:
        return f"session:{child_id}:history"

    @staticmethod
    def _used_key(child_id: str) -> str:
        return f"session:{child_id}:used_resources"

    # ── BKT State ──
    async def save_bkt_state(self, child_id: str, state: BKTState) -> None:
        key = self._state_key(child_id)
        await self._r.set(key, json.dumps(asdict(state)))
        await self._r.expire(key, SESSION_TTL)

    async def load_bkt_state(self, child_id: str) -> BKTState | None:
        raw = await self._r.get(self._state_key(child_id))
        if raw is None:
            return None
        data = json.loads(raw)
        return BKTState(**data)

    # ── Session Context ──
    async def save_session_context(
        self, child_id: str, ctx: SessionContext
    ) -> None:
        key = self._context_key(child_id)
        await self._r.set(key, json.dumps(asdict(ctx)))
        await self._r.expire(key, SESSION_TTL)

    async def load_session_context(
        self, child_id: str
    ) -> SessionContext | None:
        raw = await self._r.get(self._context_key(child_id))
        if raw is None:
            return None
        data = json.loads(raw)
        return SessionContext(**data)

    # ── EMA History ──
    async def push_session_ema(
        self, child_id: str, ema_value: float
    ) -> None:
        key = self._history_key(child_id)
        await self._r.rpush(key, str(ema_value))
        await self._r.ltrim(key, -3, -1)  # keep last 3
        await self._r.expire(key, SESSION_TTL)

    async def get_recent_emas(self, child_id: str) -> list[float]:
        raw_list = await self._r.lrange(self._history_key(child_id), 0, -1)
        return [float(v) for v in raw_list]

    # ── Used Resources (No-Repeat Rule) ──
    async def mark_resource_used(
        self, child_id: str, resource_id: str
    ) -> None:
        key = self._used_key(child_id)
        await self._r.sadd(key, resource_id)
        await self._r.expire(key, SESSION_TTL)

    async def is_resource_used(
        self, child_id: str, resource_id: str
    ) -> bool:
        return bool(
            await self._r.sismember(self._used_key(child_id), resource_id)
        )

    async def get_used_resources(self, child_id: str) -> set[str]:
        members = await self._r.smembers(self._used_key(child_id))
        return {m.decode() if isinstance(m, bytes) else m for m in members}

    # ── Session Cleanup ──
    async def clear_session(self, child_id: str) -> None:
        keys = [
            self._state_key(child_id),
            self._context_key(child_id),
            self._history_key(child_id),
            self._used_key(child_id),
        ]
        await self._r.delete(*keys)
