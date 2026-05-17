from dataclasses import dataclass
from typing import Optional
from inference_engine.schemas import (
    DiagnosticPhase,
    DiagnosticDifficulty,
    DiagnosticExitReason,
)
from inference_engine.diagnostic.state_machine import DiagnosticState, DiagnosticInteraction
from inference_engine.diagnostic.edge_cases import (
    check_basal,
    check_ceiling,
    apply_first_timeout_grace,
    next_level_after_progression,
)
from inference_engine.diagnostic.result_calculator import build_diagnostic_result
from inference_engine.diagnostic.exercise_selector import ActivityInstance
from inference_engine.rules.constants import DIAGNOSTIC_MAX_INTERACTIONS


@dataclass
class DiagnosticStepResult:
    """Result of evaluating one diagnostic response."""
    phase: DiagnosticPhase
    next_exercise: Optional[ActivityInstance] = None
    diagnostic_result: Optional[dict] = None


@dataclass
class DiagnosticResponse:
    """Incoming response from the frontend for a diagnostic interaction."""
    selected_id: str
    correct_id: str
    tra_ms: int
    is_timeout: bool
    is_correct_override: bool | None = None


def evaluate_diagnostic_response(
    state: DiagnosticState,
    response: DiagnosticResponse,
) -> DiagnosticStepResult:
    """
    Core evaluator: processes one diagnostic response and advances the state machine.

    State transitions:
        AWAITING_BASAL → EXPLORING       (basal confirmed)
        EXPLORING      → CEILING_DETECTED (3 consecutive errors)
        EXPLORING      → LIMIT_REACHED   (interaction > 15)
        CEILING_DETECTED/LIMIT_REACHED → COMPLETED

    Returns a DiagnosticStepResult indicating the new phase and,
    if completed, the final diagnostic result.
    """
    if response.is_correct_override is not None:
        is_correct = response.is_correct_override and not response.is_timeout
    else:
        is_correct = response.selected_id == response.correct_id and not response.is_timeout

    # ── Apply first-timeout grace ──
    if apply_first_timeout_grace(state, response.is_timeout):
        is_correct = False
        state.consecutive_errors = 0
        state.current_difficulty = DiagnosticDifficulty.LOW
    else:
        if is_correct:
            state.consecutive_correct += 1
            state.consecutive_errors = 0
        else:
            state.consecutive_errors += 1
            state.consecutive_correct = 0

    # ── Record interaction ──
    state.history.append(DiagnosticInteraction(
        interaction_num=state.interaction_num,
        level=state.current_test_level,
        difficulty=state.current_difficulty,
        resource_id=response.correct_id,
        correct=is_correct,
        tra_ms=response.tra_ms,
        is_timeout=response.is_timeout,
    ))
    state.used_items.append(response.correct_id)
    state.interaction_num += 1

    # ── Check exit conditions (ceiling) ──
    if check_ceiling(state):
        state.ceiling_detected = True
        state.ceiling_level = state.current_test_level
        state.phase = DiagnosticPhase.CEILING_DETECTED
        result = build_diagnostic_result(state, DiagnosticExitReason.CEILING)
        state.phase = DiagnosticPhase.COMPLETED
        return DiagnosticStepResult(
            phase=DiagnosticPhase.COMPLETED,
            diagnostic_result=result,
        )

    # ── Check exit conditions (interaction limit) ──
    if state.interaction_num > DIAGNOSTIC_MAX_INTERACTIONS:
        state.phase = DiagnosticPhase.LIMIT_REACHED
        result = build_diagnostic_result(state, DiagnosticExitReason.LIMIT_REACHED)
        state.phase = DiagnosticPhase.COMPLETED
        return DiagnosticStepResult(
            phase=DiagnosticPhase.COMPLETED,
            diagnostic_result=result,
        )

    # ── Check basal (only in AWAITING_BASAL phase) ──
    if not state.basal_established and check_basal(state):
        state.basal_established = True
        state.basal_level = state.current_test_level
        state.current_test_level = min(5, state.basal_level + 1)
        state.current_difficulty = DiagnosticDifficulty.LOW
        state.consecutive_correct = 0
        state.phase = DiagnosticPhase.EXPLORING
        return DiagnosticStepResult(phase=DiagnosticPhase.EXPLORING)

    # ── Normal progression (EXPLORING phase) ──
    if state.basal_established:
        new_level, new_difficulty = next_level_after_progression(state)
        state.current_test_level = new_level
        state.current_difficulty = new_difficulty
        state.phase = DiagnosticPhase.EXPLORING
    else:
        state.phase = DiagnosticPhase.AWAITING_BASAL

    return DiagnosticStepResult(phase=state.phase)
