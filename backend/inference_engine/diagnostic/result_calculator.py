from inference_engine.diagnostic.state_machine import DiagnosticState
from inference_engine.schemas import DiagnosticExitReason
from inference_engine.bkt.calibrator import P_L0_BY_LEVEL


def calculate_detected_level(state: DiagnosticState, reason: DiagnosticExitReason) -> int:
    """
    Determines the child's actual competence level from the diagnostic history.

    CEILING:       level = current_test_level - 1 (last level where child succeeded)
    LIMIT_REACHED: level = highest level with at least 1 correct answer
    """
    if reason == DiagnosticExitReason.CEILING:
        return max(1, state.current_test_level - 1)

    if reason == DiagnosticExitReason.LIMIT_REACHED:
        levels_with_correct = [r.level for r in state.history if r.correct]
        return max(levels_with_correct) if levels_with_correct else 1

    return state.current_test_level


def get_initial_p_l0(detected_level: int) -> float:
    """Returns the initial P(L0) for BKT based on the detected level."""
    return P_L0_BY_LEVEL.get(detected_level, 0.05)


def build_diagnostic_result(
    state: DiagnosticState,
    reason: DiagnosticExitReason
) -> dict:
    """
    Builds the final diagnostic result payload.
    This data is persisted to PostgreSQL and returned to the frontend.
    """
    detected_level = calculate_detected_level(state, reason)
    p_l0 = get_initial_p_l0(detected_level)

    return {
        "child_id": state.child_id,
        "detected_level": detected_level,
        "p_l0_initial": p_l0,
        "total_interactions": state.interaction_num,
        "exit_reason": reason,
        "basal_level": state.basal_level,
        "ceiling_level": state.ceiling_level,
        "history": state.history,
    }
