import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from inference_engine.bkt.engine import update
from inference_engine.rules.constants import P_TRANSIT, P_SLIP, P_MASTERY_THRESHOLD


class TestBKTUpdate:
    """Tests for the core BKT Bayesian update formula."""

    def test_correct_answer_increases_mastery(self):
        p_initial = 0.30
        p_after = update(p_mastery=p_initial, correct=True)
        assert p_after > p_initial

    def test_wrong_answer_decreases_mastery(self):
        p_initial = 0.50
        p_after = update(p_mastery=p_initial, correct=False)
        assert p_after < p_initial

    def test_mastery_never_exceeds_one(self):
        p = 0.99
        for _ in range(50):
            p = update(p_mastery=p, correct=True)
        assert p <= 1.0

    def test_mastery_never_below_zero(self):
        p = 0.01
        for _ in range(50):
            p = update(p_mastery=p, correct=False)
        assert p >= 0.0

    def test_repeated_correct_reaches_mastery_threshold(self):
        p = 0.10
        for _ in range(20):
            p = update(p_mastery=p, correct=True)
        assert p >= P_MASTERY_THRESHOLD

    def test_high_guess_dampens_correct_increase(self):
        """With high P(G), correct answers should increase P(L) less."""
        p_low_guess = update(p_mastery=0.30, correct=True, p_guess=0.05)
        p_high_guess = update(p_mastery=0.30, correct=True, p_guess=0.50)
        assert p_low_guess > p_high_guess

    def test_zero_mastery_correct_still_increases(self):
        p_after = update(p_mastery=0.0, correct=True)
        assert p_after > 0.0

    def test_near_full_mastery_wrong_decreases(self):
        """P(L)=1.0 is an absorbing state in BKT, so we test with 0.99."""
        p_after = update(p_mastery=0.99, correct=False)
        assert p_after < 0.99

    def test_voice_exercise_no_guess(self):
        """V-M exercises have P(G)=0, so correct answers are very informative."""
        p_voice = update(p_mastery=0.20, correct=True, p_guess=0.00)
        p_touch = update(p_mastery=0.20, correct=True, p_guess=0.25)
        assert p_voice > p_touch

    def test_default_parameters_used(self):
        """Ensure defaults from constants are applied when not specified."""
        p_after = update(p_mastery=0.30, correct=True)
        p_explicit = update(
            p_mastery=0.30, correct=True,
            p_transit=P_TRANSIT, p_slip=P_SLIP, p_guess=0.33
        )
        assert p_after == p_explicit


class TestBKTCalibrator:
    """Tests for P(L0) calibration from diagnostic results."""

    def test_all_five_levels_have_p_l0(self):
        from inference_engine.bkt.calibrator import P_L0_BY_LEVEL
        for level in range(1, 6):
            assert level in P_L0_BY_LEVEL
            assert 0.0 < P_L0_BY_LEVEL[level] < 1.0

    def test_p_l0_increases_with_level(self):
        from inference_engine.bkt.calibrator import P_L0_BY_LEVEL
        for level in range(1, 5):
            assert P_L0_BY_LEVEL[level] < P_L0_BY_LEVEL[level + 1]

    def test_calibrate_hito_below_detected(self):
        from inference_engine.bkt.calibrator import calibrate_hito_state
        state = calibrate_hito_state("H_N1_001", detected_level=3, hito_level=1)
        assert state.p_mastery == 0.90
        assert state.is_mastered is True

    def test_calibrate_hito_at_detected(self):
        from inference_engine.bkt.calibrator import calibrate_hito_state
        state = calibrate_hito_state("H_N3_001", detected_level=3, hito_level=3)
        assert state.p_mastery == 0.25
        assert state.is_mastered is False

    def test_calibrate_hito_above_detected(self):
        from inference_engine.bkt.calibrator import calibrate_hito_state
        state = calibrate_hito_state("H_N5_001", detected_level=3, hito_level=5)
        assert state.p_mastery == 0.05
        assert state.is_mastered is False

    def test_get_initial_p_l0_invalid_level_defaults(self):
        from inference_engine.bkt.calibrator import get_initial_p_l0
        assert get_initial_p_l0(99) == 0.05
