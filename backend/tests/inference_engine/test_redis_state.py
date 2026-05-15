import pytest
import pytest_asyncio
import fakeredis.aioredis

from inference_engine.schemas import BKTState, SessionContext
from inference_engine.persistence.redis_state import RedisStateManager


@pytest_asyncio.fixture
async def mgr():
    redis = fakeredis.aioredis.FakeRedis()
    yield RedisStateManager(redis)
    await redis.aclose()


class TestBKTState:
    @pytest.mark.asyncio
    async def test_save_and_load(self, mgr):
        state = BKTState(
            hito_id="H_N1_001",
            p_mastery=0.42,
            p_transit=0.20,
            p_slip=0.10,
            p_guess=0.33,
        )
        await mgr.save_bkt_state("child_1", state)
        loaded = await mgr.load_bkt_state("child_1")
        assert loaded is not None
        assert loaded.hito_id == "H_N1_001"
        assert loaded.p_mastery == pytest.approx(0.42)
        assert loaded.p_transit == pytest.approx(0.20)

    @pytest.mark.asyncio
    async def test_load_nonexistent(self, mgr):
        loaded = await mgr.load_bkt_state("no_child")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_overwrite(self, mgr):
        s1 = BKTState(hito_id="H1", p_mastery=0.30)
        s2 = BKTState(hito_id="H2", p_mastery=0.90)
        await mgr.save_bkt_state("child_1", s1)
        await mgr.save_bkt_state("child_1", s2)
        loaded = await mgr.load_bkt_state("child_1")
        assert loaded.hito_id == "H2"
        assert loaded.p_mastery == pytest.approx(0.90)


class TestSessionContext:
    @pytest.mark.asyncio
    async def test_save_and_load(self, mgr):
        ctx = SessionContext(
            level=2,
            consecutive_correct=3,
            consecutive_errors=0,
            consecutive_timeouts=0,
            exercises_done=5,
            elapsed_minutes=8.5,
        )
        await mgr.save_session_context("child_1", ctx)
        loaded = await mgr.load_session_context("child_1")
        assert loaded is not None
        assert loaded.level == 2
        assert loaded.consecutive_correct == 3
        assert loaded.elapsed_minutes == pytest.approx(8.5)

    @pytest.mark.asyncio
    async def test_load_nonexistent(self, mgr):
        loaded = await mgr.load_session_context("no_child")
        assert loaded is None


class TestEMAHistory:
    @pytest.mark.asyncio
    async def test_push_and_get(self, mgr):
        await mgr.push_session_ema("child_1", 82.5)
        await mgr.push_session_ema("child_1", 74.0)
        emas = await mgr.get_recent_emas("child_1")
        assert emas == [pytest.approx(82.5), pytest.approx(74.0)]

    @pytest.mark.asyncio
    async def test_keeps_last_3(self, mgr):
        for v in [80.0, 70.0, 60.0, 50.0]:
            await mgr.push_session_ema("child_1", v)
        emas = await mgr.get_recent_emas("child_1")
        assert len(emas) == 3
        assert emas == [pytest.approx(70.0), pytest.approx(60.0), pytest.approx(50.0)]

    @pytest.mark.asyncio
    async def test_empty_history(self, mgr):
        emas = await mgr.get_recent_emas("no_child")
        assert emas == []


class TestUsedResources:
    @pytest.mark.asyncio
    async def test_mark_and_check(self, mgr):
        await mgr.mark_resource_used("child_1", "W_001")
        assert await mgr.is_resource_used("child_1", "W_001") is True
        assert await mgr.is_resource_used("child_1", "W_002") is False

    @pytest.mark.asyncio
    async def test_multiple_resources(self, mgr):
        await mgr.mark_resource_used("child_1", "W_001")
        await mgr.mark_resource_used("child_1", "W_045")
        assert await mgr.is_resource_used("child_1", "W_001") is True
        assert await mgr.is_resource_used("child_1", "W_045") is True

    @pytest.mark.asyncio
    async def test_not_used_for_other_child(self, mgr):
        await mgr.mark_resource_used("child_1", "W_001")
        assert await mgr.is_resource_used("child_2", "W_001") is False


class TestClearSession:
    @pytest.mark.asyncio
    async def test_clears_all_keys(self, mgr):
        state = BKTState(hito_id="H1", p_mastery=0.5)
        ctx = SessionContext(
            level=1, consecutive_correct=0,
            consecutive_errors=0, consecutive_timeouts=0,
            exercises_done=0, elapsed_minutes=0.0,
        )
        await mgr.save_bkt_state("child_1", state)
        await mgr.save_session_context("child_1", ctx)
        await mgr.push_session_ema("child_1", 75.0)
        await mgr.mark_resource_used("child_1", "W_001")

        await mgr.clear_session("child_1")

        assert await mgr.load_bkt_state("child_1") is None
        assert await mgr.load_session_context("child_1") is None
        assert await mgr.get_recent_emas("child_1") == []
        assert await mgr.is_resource_used("child_1", "W_001") is False
