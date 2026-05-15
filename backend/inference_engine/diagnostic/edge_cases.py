from inference_engine.diagnostic.state_machine import DiagnosticState
from inference_engine.schemas import DiagnosticDifficulty
from inference_engine.rules.constants import (
    DIAGNOSTIC_BASAL_STREAK,
    DIAGNOSTIC_BASAL_TRA_LIMIT_MS,
    DIAGNOSTIC_CEILING_STREAK
)


def check_basal(state: DiagnosticState) -> bool:
    """
    Returns True if basal (floor) is established.
    Condition: 3 consecutive correct answers with TRA < 4000ms each.
    """
    if state.basal_established:
        return True

    if len(state.history) < DIAGNOSTIC_BASAL_STREAK:
        return False

    last_n = state.history[-DIAGNOSTIC_BASAL_STREAK:]
    return all(
        r.correct and r.tra_ms < DIAGNOSTIC_BASAL_TRA_LIMIT_MS
        for r in last_n
    )


def check_ceiling(state: DiagnosticState) -> bool:
    """
    Returns True if ceiling is detected.
    Condition: 3 consecutive errors or timeouts.
    """
    if len(state.history) < DIAGNOSTIC_CEILING_STREAK:
        return False

    last_n = state.history[-DIAGNOSTIC_CEILING_STREAK:]
    return all(
        not r.correct or r.is_timeout
        for r in last_n
    )


def apply_first_timeout_grace(state: DiagnosticState, is_timeout: bool) -> bool:
    """
    Returns True if the first-timeout grace rule should activate.
    The first interaction's timeout does NOT count toward the error streak.
    """
    return state.interaction_num == 1 and is_timeout


def next_level_after_progression(state: DiagnosticState) -> tuple[int, DiagnosticDifficulty]:
    """
    Determines the next (level, difficulty) after a normal response
    in the EXPLORING phase.

    Rules:
      - 2 consecutive correct → advance to next level, start at LOW difficulty
      - 1 error → drop difficulty within same level (HIGH→MEDIUM→LOW)
      - Otherwise → keep current
    """
    if state.consecutive_correct >= 2:
        new_level = min(5, state.current_test_level + 1)
        return (new_level, DiagnosticDifficulty.LOW)

    if state.consecutive_errors == 1:
        difficulty_drop = {
            DiagnosticDifficulty.HIGH: DiagnosticDifficulty.MEDIUM,
            DiagnosticDifficulty.MEDIUM: DiagnosticDifficulty.LOW,
            DiagnosticDifficulty.LOW: DiagnosticDifficulty.LOW,
        }
        return (state.current_test_level, difficulty_drop[state.current_difficulty])

    return (state.current_test_level, state.current_difficulty)
