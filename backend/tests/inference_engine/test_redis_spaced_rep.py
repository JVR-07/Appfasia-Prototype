import time
import pytest
import pytest_asyncio
import fakeredis.aioredis

from inference_engine.persistence.redis_spaced_rep import (
    RedisSpacedRepManager
)


@pytest_asyncio.fixture
async def mgr():
    redis = fakeredis.aioredis.FakeRedis()
    yield RedisSpacedRepManager(redis)
    await redis.aclose()


class TestEnqueueHito:
    @pytest.mark.asyncio
    async def test_enqueue_creates_queue_entry(self, mgr):
        await mgr.enqueue_hito("child_1", "H_N1_001", stage=1)
        stats = await mgr.get_queue_stats("child_1")
        assert stats["total"] == 1

    @pytest.mark.asyncio
    async def test_enqueue_creates_meta(self, mgr):
        await mgr.enqueue_hito("child_1", "H_N1_001", stage=2)
        meta = await mgr._r.hgetall(
            mgr._meta_key("child_1", "H_N1_001")
        )
        assert meta is not None
        stage = meta.get(b"stage", meta.get("stage"))
        assert int(stage) == 2

    @pytest.mark.asyncio
    async def test_enqueue_multiple(self, mgr):
        await mgr.enqueue_hito("child_1", "H1")
        await mgr.enqueue_hito("child_1", "H2")
        await mgr.enqueue_hito("child_1", "H3")
        stats = await mgr.get_queue_stats("child_1")
        assert stats["total"] == 3


class TestGetPendingReviews:
    @pytest.mark.asyncio
    async def test_returns_due_reviews(self, mgr):
        await mgr.enqueue_hito("child_1", "H1", stage=1)
        far_future = time.time() + 200_000
        reviews = await mgr.get_pending_reviews("child_1", now_ts=far_future)
        assert len(reviews) == 1
        assert reviews[0]["hito_id"] == "H1"
        assert reviews[0]["stage"] == 1

    @pytest.mark.asyncio
    async def test_excludes_not_due(self, mgr):
        await mgr.enqueue_hito("child_1", "H1", stage=1)
        now = time.time()
        reviews = await mgr.get_pending_reviews("child_1", now_ts=now)
        assert len(reviews) == 0

    @pytest.mark.asyncio
    async def test_empty_queue(self, mgr):
        reviews = await mgr.get_pending_reviews("child_1")
        assert reviews == []

    @pytest.mark.asyncio
    async def test_sorted_by_timestamp(self, mgr):
        await mgr.enqueue_hito("child_1", "H1", stage=1)
        await mgr.enqueue_hito("child_1", "H2", stage=2)
        far_future = time.time() + 1_000_000
        reviews = await mgr.get_pending_reviews("child_1", now_ts=far_future)
        assert len(reviews) == 2
        # Stage 1 has shorter interval, so H1 should be due first
        assert reviews[0]["next_review_ts"] <= reviews[1]["next_review_ts"]


class TestAdvanceStage:
    @pytest.mark.asyncio
    async def test_pass_advances_stage(self, mgr):
        await mgr.enqueue_hito("child_1", "H1", stage=1)
        graduated = await mgr.advance_stage("child_1", "H1", ipf=80.0)
        assert graduated is False

        far_future = time.time() + 1_000_000
        reviews = await mgr.get_pending_reviews("child_1", now_ts=far_future)
        assert len(reviews) == 1
        assert reviews[0]["stage"] == 2

    @pytest.mark.asyncio
    async def test_fail_resets_to_stage_1(self, mgr):
        await mgr.enqueue_hito("child_1", "H1", stage=3)
        graduated = await mgr.advance_stage("child_1", "H1", ipf=40.0)
        assert graduated is False

        far_future = time.time() + 1_000_000
        reviews = await mgr.get_pending_reviews("child_1", now_ts=far_future)
        assert reviews[0]["stage"] == 1

    @pytest.mark.asyncio
    async def test_pass_stage_4_graduates(self, mgr):
        await mgr.enqueue_hito("child_1", "H1", stage=4)
        graduated = await mgr.advance_stage("child_1", "H1", ipf=75.0)
        assert graduated is True

        stats = await mgr.get_queue_stats("child_1")
        assert stats["total"] == 0

    @pytest.mark.asyncio
    async def test_nonexistent_hito(self, mgr):
        result = await mgr.advance_stage("child_1", "NONE", ipf=80.0)
        assert result is False


class TestGraduateHito:
    @pytest.mark.asyncio
    async def test_removes_from_queue(self, mgr):
        await mgr.enqueue_hito("child_1", "H1")
        await mgr.enqueue_hito("child_1", "H2")
        await mgr.graduate_hito("child_1", "H1")

        stats = await mgr.get_queue_stats("child_1")
        assert stats["total"] == 1

    @pytest.mark.asyncio
    async def test_removes_meta(self, mgr):
        await mgr.enqueue_hito("child_1", "H1")
        await mgr.graduate_hito("child_1", "H1")

        exists = await mgr._r.exists(mgr._meta_key("child_1", "H1"))
        assert exists == 0


class TestQueueStats:
    @pytest.mark.asyncio
    async def test_empty_stats(self, mgr):
        stats = await mgr.get_queue_stats("child_1")
        assert stats["total"] == 0
        assert stats["due_now"] == 0

    @pytest.mark.asyncio
    async def test_due_count(self, mgr):
        await mgr.enqueue_hito("child_1", "H1", stage=1)
        await mgr.enqueue_hito("child_1", "H2", stage=1)

        stats = await mgr.get_queue_stats("child_1")
        assert stats["total"] == 2
        assert stats["due_now"] == 0  # not due yet


class TestIsolation:
    @pytest.mark.asyncio
    async def test_different_children_isolated(self, mgr):
        await mgr.enqueue_hito("child_1", "H1")
        await mgr.enqueue_hito("child_2", "H2")

        stats_1 = await mgr.get_queue_stats("child_1")
        stats_2 = await mgr.get_queue_stats("child_2")
        assert stats_1["total"] == 1
        assert stats_2["total"] == 1
