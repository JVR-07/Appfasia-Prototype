import time

from inference_engine.memory.spaced_repetition import (
    REVIEW_INTERVALS,
    MASTERY_THRESHOLD_FOR_QUEUE,
    REVIEW_FAIL_IPF_THRESHOLD,
    GRADUATION_STAGE,
    compute_next_review_timestamp,
    should_enqueue,
    process_review_result,
    pick_reviews_for_session,
)


NOW = 1_700_000_000.0  # fixed timestamp for deterministic tests


class TestComputeNextReviewTimestamp:
    def test_stage_1_interval(self):
        ts = compute_next_review_timestamp(1, NOW)
        assert ts == NOW + (24 * 3600)

    def test_stage_2_interval(self):
        ts = compute_next_review_timestamp(2, NOW)
        assert ts == NOW + (72 * 3600)

    def test_stage_3_interval(self):
        ts = compute_next_review_timestamp(3, NOW)
        assert ts == NOW + (168 * 3600)

    def test_stage_4_interval(self):
        ts = compute_next_review_timestamp(4, NOW)
        assert ts == NOW + (504 * 3600)

    def test_defaults_to_now(self):
        before = time.time()
        ts = compute_next_review_timestamp(1)
        after = time.time()
        expected_min = before + (24 * 3600)
        expected_max = after + (24 * 3600)
        assert expected_min <= ts <= expected_max

    def test_unknown_stage_uses_graduation(self):
        ts = compute_next_review_timestamp(99, NOW)
        assert ts == NOW + (REVIEW_INTERVALS[GRADUATION_STAGE] * 3600)


class TestShouldEnqueue:
    def test_above_threshold(self):
        assert should_enqueue(0.90) is True

    def test_at_threshold(self):
        assert should_enqueue(MASTERY_THRESHOLD_FOR_QUEUE) is True

    def test_below_threshold(self):
        assert should_enqueue(0.80) is False

    def test_zero(self):
        assert should_enqueue(0.0) is False


class TestProcessReviewResult:
    def test_pass_stage_1_advances(self):
        new_stage, graduated = process_review_result(1, 80.0)
        assert new_stage == 2
        assert graduated is False

    def test_pass_stage_3_advances(self):
        new_stage, graduated = process_review_result(3, 65.0)
        assert new_stage == 4
        assert graduated is False

    def test_pass_stage_4_graduates(self):
        new_stage, graduated = process_review_result(4, 70.0)
        assert new_stage == 4
        assert graduated is True

    def test_fail_resets_to_stage_1(self):
        new_stage, graduated = process_review_result(3, 55.0)
        assert new_stage == 1
        assert graduated is False

    def test_fail_at_boundary(self):
        new_stage, graduated = process_review_result(
            2, REVIEW_FAIL_IPF_THRESHOLD - 0.1
        )
        assert new_stage == 1

    def test_pass_at_boundary(self):
        new_stage, graduated = process_review_result(
            2, REVIEW_FAIL_IPF_THRESHOLD
        )
        assert new_stage == 3

    def test_fail_at_stage_1_stays(self):
        new_stage, graduated = process_review_result(1, 40.0)
        assert new_stage == 1
        assert graduated is False


class TestPickReviewsForSession:
    def test_picks_due_reviews(self):
        pending = [
            {"hito_id": "H1", "next_review_ts": NOW - 100, "stage": 1},
            {"hito_id": "H2", "next_review_ts": NOW - 50, "stage": 2},
        ]
        result = pick_reviews_for_session(pending, NOW)
        assert result == ["H1", "H2"]

    def test_respects_max_count(self):
        pending = [
            {"hito_id": "H1", "next_review_ts": NOW - 100, "stage": 1},
            {"hito_id": "H2", "next_review_ts": NOW - 50, "stage": 2},
            {"hito_id": "H3", "next_review_ts": NOW - 10, "stage": 1},
        ]
        result = pick_reviews_for_session(pending, NOW, max_count=2)
        assert len(result) == 2

    def test_excludes_not_yet_due(self):
        pending = [
            {"hito_id": "H1", "next_review_ts": NOW - 100, "stage": 1},
            {"hito_id": "H2", "next_review_ts": NOW + 1000, "stage": 2},
        ]
        result = pick_reviews_for_session(pending, NOW)
        assert result == ["H1"]

    def test_empty_pending(self):
        result = pick_reviews_for_session([], NOW)
        assert result == []

    def test_none_due(self):
        pending = [
            {"hito_id": "H1", "next_review_ts": NOW + 1000, "stage": 1},
        ]
        result = pick_reviews_for_session(pending, NOW)
        assert result == []

    def test_oldest_first(self):
        pending = [
            {"hito_id": "H2", "next_review_ts": NOW - 10, "stage": 1},
            {"hito_id": "H1", "next_review_ts": NOW - 100, "stage": 1},
        ]
        result = pick_reviews_for_session(pending, NOW)
        assert result == ["H1", "H2"]

    def test_at_boundary_included(self):
        pending = [
            {"hito_id": "H1", "next_review_ts": NOW, "stage": 1},
        ]
        result = pick_reviews_for_session(pending, NOW)
        assert result == ["H1"]
