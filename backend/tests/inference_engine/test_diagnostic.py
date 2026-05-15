import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from inference_engine.schemas import (
    DiagnosticPhase,
    DiagnosticDifficulty,
    DiagnosticExitReason,
)
from inference_engine.diagnostic.state_machine import DiagnosticState
from inference_engine.diagnostic.level_calculator import (
    expected_level,
    start_level,
)
from inference_engine.diagnostic.edge_cases import (
    check_basal,
    check_ceiling,
    apply_first_timeout_grace,
    next_level_after_progression,
)
from inference_engine.diagnostic.result_calculator import (
    calculate_detected_level,
    get_initial_p_l0,
)
from inference_engine.diagnostic.evaluator import (
    evaluate_diagnostic_response,
    DiagnosticResponse,
)
from inference_engine.diagnostic.state_machine import DiagnosticInteraction


# ──────────────────────────────────────────────
# Level Calculator
# ──────────────────────────────────────────────

class TestLevelCalculator:
    def test_age_12_months_level_1(self):
        assert expected_level(12) == 1

    def test_age_36_months_level_2(self):
        assert expected_level(36) == 2

    def test_age_60_months_level_3(self):
        assert expected_level(60) == 3

    def test_age_84_months_level_4(self):
        assert expected_level(84) == 4

    def test_age_108_months_level_5(self):
        assert expected_level(108) == 5

    def test_start_level_from_1(self):
        level, diff = start_level(1)
        assert level == 1
        assert diff == DiagnosticDifficulty.LOW

    def test_start_level_from_3(self):
        level, diff = start_level(3)
        assert level == 2
        assert diff == DiagnosticDifficulty.HIGH

    def test_start_level_from_5(self):
        level, diff = start_level(5)
        assert level == 4
        assert diff == DiagnosticDifficulty.HIGH


# ──────────────────────────────────────────────
# Edge Cases (pure functions)
# ──────────────────────────────────────────────

def _make_state(**overrides) -> DiagnosticState:
    """Helper to create a DiagnosticState with defaults."""
    defaults = {
        "session_diag_id": "diag-test-001",
        "child_id": "child-test-001",
    }
    defaults.update(overrides)
    return DiagnosticState(**defaults)


def _make_interaction(correct: bool, tra_ms: int = 2500, is_timeout: bool = False, level: int = 1) -> DiagnosticInteraction:
    return DiagnosticInteraction(
        interaction_num=0,
        level=level,
        difficulty=DiagnosticDifficulty.HIGH,
        resource_id="W_001",
        correct=correct,
        tra_ms=tra_ms,
        is_timeout=is_timeout,
    )


class TestCheckBasal:
    def test_three_correct_under_4s_establishes_basal(self):
        state = _make_state(history=[
            _make_interaction(True, 2500),
            _make_interaction(True, 3000),
            _make_interaction(True, 3500),
        ])
        assert check_basal(state) is True

    def test_one_incorrect_breaks_basal(self):
        state = _make_state(history=[
            _make_interaction(True, 2500),
            _make_interaction(False, 3000),
            _make_interaction(True, 3500),
        ])
        assert check_basal(state) is False

    def test_tra_over_4s_breaks_basal(self):
        state = _make_state(history=[
            _make_interaction(True, 2500),
            _make_interaction(True, 4500),
            _make_interaction(True, 3500),
        ])
        assert check_basal(state) is False

    def test_already_established_returns_true(self):
        state = _make_state(basal_established=True)
        assert check_basal(state) is True

    def test_insufficient_history(self):
        state = _make_state(history=[_make_interaction(True)])
        assert check_basal(state) is False


class TestCheckCeiling:
    def test_three_errors_triggers_ceiling(self):
        state = _make_state(history=[
            _make_interaction(False),
            _make_interaction(False),
            _make_interaction(False),
        ])
        assert check_ceiling(state) is True

    def test_three_timeouts_triggers_ceiling(self):
        state = _make_state(history=[
            _make_interaction(False, is_timeout=True),
            _make_interaction(False, is_timeout=True),
            _make_interaction(False, is_timeout=True),
        ])
        assert check_ceiling(state) is True

    def test_one_correct_breaks_ceiling(self):
        state = _make_state(history=[
            _make_interaction(False),
            _make_interaction(True),
            _make_interaction(False),
        ])
        assert check_ceiling(state) is False

    def test_insufficient_history(self):
        state = _make_state(history=[_make_interaction(False)])
        assert check_ceiling(state) is False


class TestFirstTimeoutGrace:
    def test_first_interaction_timeout_is_grace(self):
        state = _make_state(interaction_num=1)
        assert apply_first_timeout_grace(state, True) is True

    def test_first_interaction_no_timeout_no_grace(self):
        state = _make_state(interaction_num=1)
        assert apply_first_timeout_grace(state, False) is False

    def test_second_interaction_timeout_no_grace(self):
        state = _make_state(interaction_num=2)
        assert apply_first_timeout_grace(state, True) is False


class TestNextLevelAfterProgression:
    def test_two_correct_advances_level(self):
        state = _make_state(
            consecutive_correct=2,
            consecutive_errors=0,
            current_test_level=2,
        )
        level, diff = next_level_after_progression(state)
        assert level == 3
        assert diff == DiagnosticDifficulty.LOW

    def test_cannot_exceed_level_5(self):
        state = _make_state(
            consecutive_correct=2,
            consecutive_errors=0,
            current_test_level=5,
        )
        level, _ = next_level_after_progression(state)
        assert level == 5

    def test_one_error_drops_difficulty(self):
        state = _make_state(
            consecutive_correct=0,
            consecutive_errors=1,
            current_test_level=3,
            current_difficulty=DiagnosticDifficulty.HIGH,
        )
        level, diff = next_level_after_progression(state)
        assert level == 3
        assert diff == DiagnosticDifficulty.MEDIUM

    def test_low_difficulty_stays_low(self):
        state = _make_state(
            consecutive_correct=0,
            consecutive_errors=1,
            current_test_level=3,
            current_difficulty=DiagnosticDifficulty.LOW,
        )
        _, diff = next_level_after_progression(state)
        assert diff == DiagnosticDifficulty.LOW


# ──────────────────────────────────────────────
# Result Calculator
# ──────────────────────────────────────────────

class TestResultCalculator:
    def test_ceiling_detected_level(self):
        state = _make_state(current_test_level=4)
        level = calculate_detected_level(state, DiagnosticExitReason.CEILING)
        assert level == 3

    def test_ceiling_never_below_1(self):
        state = _make_state(current_test_level=1)
        level = calculate_detected_level(state, DiagnosticExitReason.CEILING)
        assert level == 1

    def test_limit_reached_uses_highest_correct(self):
        state = _make_state(
            current_test_level=4,
            history=[
                _make_interaction(True, level=2),
                _make_interaction(False, level=3),
                _make_interaction(True, level=3),
                _make_interaction(False, level=4),
            ],
        )
        level = calculate_detected_level(state, DiagnosticExitReason.LIMIT_REACHED)
        assert level == 3

    def test_limit_reached_no_correct_defaults_to_1(self):
        state = _make_state(
            history=[_make_interaction(False, level=2)],
        )
        level = calculate_detected_level(state, DiagnosticExitReason.LIMIT_REACHED)
        assert level == 1

    def test_p_l0_for_all_levels(self):
        for level in range(1, 6):
            p = get_initial_p_l0(level)
            assert 0.0 < p < 1.0


# ──────────────────────────────────────────────
# Evaluator (integration-level)
# ──────────────────────────────────────────────

class TestEvaluator:
    def _respond(self, state, correct=True, tra_ms=2500, is_timeout=False):
        """Helper to simulate a response through the evaluator."""
        return evaluate_diagnostic_response(
            state,
            DiagnosticResponse(
                selected_id="W_001" if correct else "W_999",
                correct_id="W_001",
                tra_ms=tra_ms,
                is_timeout=is_timeout,
            ),
        )

    def test_basal_established_after_3_correct(self):
        state = _make_state(
            phase=DiagnosticPhase.AWAITING_BASAL,
            current_test_level=1,
            current_difficulty=DiagnosticDifficulty.HIGH,
        )
        self._respond(state, correct=True, tra_ms=2000)
        self._respond(state, correct=True, tra_ms=2000)
        result = self._respond(state, correct=True, tra_ms=2000)
        assert state.basal_established is True
        assert state.basal_level == 1
        assert result.phase == DiagnosticPhase.EXPLORING

    def test_ceiling_after_3_errors(self):
        state = _make_state(
            phase=DiagnosticPhase.EXPLORING,
            basal_established=True,
            basal_level=1,
            current_test_level=3,
            interaction_num=5,
        )
        self._respond(state, correct=False)
        self._respond(state, correct=False)
        result = self._respond(state, correct=False)
        assert result.phase == DiagnosticPhase.COMPLETED
        assert result.diagnostic_result is not None
        assert result.diagnostic_result["exit_reason"] == DiagnosticExitReason.CEILING

    def test_limit_reached_at_16_interactions(self):
        state = _make_state(
            phase=DiagnosticPhase.EXPLORING,
            basal_established=True,
            basal_level=1,
            current_test_level=3,
            interaction_num=15,
        )
        result = self._respond(state, correct=True)
        assert result.phase == DiagnosticPhase.COMPLETED
        assert result.diagnostic_result["exit_reason"] == DiagnosticExitReason.LIMIT_REACHED

    def test_first_timeout_grace(self):
        state = _make_state(
            phase=DiagnosticPhase.AWAITING_BASAL,
            interaction_num=1,
            current_test_level=1,
        )
        self._respond(state, correct=False, is_timeout=True)
        # First timeout is forgiven — error streak should be 0
        assert state.consecutive_errors == 0
        assert state.current_difficulty == DiagnosticDifficulty.LOW

    def test_full_scenario_basal_then_ceiling(self):
        """Simulate: 3 correct (basal) → advance → 3 errors (ceiling)."""
        state = _make_state(
            phase=DiagnosticPhase.AWAITING_BASAL,
            current_test_level=2,
            current_difficulty=DiagnosticDifficulty.HIGH,
        )
        # 3 correct → basal at level 2
        self._respond(state, correct=True, tra_ms=2000)
        self._respond(state, correct=True, tra_ms=2000)
        result = self._respond(state, correct=True, tra_ms=2000)
        assert state.basal_established is True
        assert state.current_test_level == 3

        # 3 errors → ceiling
        self._respond(state, correct=False)
        self._respond(state, correct=False)
        result = self._respond(state, correct=False)
        assert result.phase == DiagnosticPhase.COMPLETED
        assert result.diagnostic_result["detected_level"] == 2
