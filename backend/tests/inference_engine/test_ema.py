# pyrefly: ignore [missing-import]
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from inference_engine.memory.ema import compute_ema, should_level_down
from inference_engine.rules.constants import EMA_WEIGHT_R0, EMA_WEIGHT_R1


class TestComputeEMA:
    def test_single_session(self):
        """With only R0, EMA equals R0."""
        assert compute_ema(80.0, None, None) == 80.0

    def test_two_sessions_renormalized(self):
        """With R0 and R1, weights are renormalized to sum to 1.0."""
        ema = compute_ema(80.0, 60.0, None)
        total_w = EMA_WEIGHT_R0 + EMA_WEIGHT_R1
        expected = (80.0 * EMA_WEIGHT_R0 / total_w) + (60.0 * EMA_WEIGHT_R1 / total_w)
        assert ema == pytest.approx(expected)

    def test_three_sessions_full_formula(self):
        """Standard EMA: (R0*0.5) + (R1*0.3) + (R2*0.2)."""
        ema = compute_ema(90.0, 70.0, 50.0)
        expected = (90.0 * 0.5) + (70.0 * 0.3) + (50.0 * 0.2)
        assert ema == pytest.approx(expected)

    def test_recent_session_has_most_weight(self):
        """R0 (w=0.5) should outweigh any individual past session (R1=0.3, R2=0.2)."""
        ema_high_r0 = compute_ema(100.0, 50.0, 70.0)
        ema_low_r0 = compute_ema(50.0, 100.0, 70.0)
        assert ema_high_r0 > ema_low_r0

    def test_all_equal_sessions(self):
        ema = compute_ema(75.0, 75.0, 75.0)
        assert ema == pytest.approx(75.0)

    def test_perfect_sessions(self):
        ema = compute_ema(100.0, 100.0, 100.0)
        assert ema == pytest.approx(100.0)


class TestShouldLevelDown:
    def test_three_below_threshold_triggers(self):
        assert should_level_down([40.0, 45.0, 30.0]) is True

    def test_one_above_threshold_does_not_trigger(self):
        assert should_level_down([40.0, 55.0, 30.0]) is False

    def test_insufficient_data_does_not_trigger(self):
        assert should_level_down([40.0, 30.0]) is False

    def test_empty_list_does_not_trigger(self):
        assert should_level_down([]) is False

    def test_exactly_at_threshold_does_not_trigger(self):
        """IPF_PRACTICE_LOW is 50.0, so values at 50 should NOT trigger."""
        assert should_level_down([50.0, 50.0, 50.0]) is False

    def test_uses_last_three_only(self):
        """Only the last 3 values matter, earlier ones are ignored."""
        assert should_level_down([80.0, 80.0, 40.0, 30.0, 20.0]) is True
