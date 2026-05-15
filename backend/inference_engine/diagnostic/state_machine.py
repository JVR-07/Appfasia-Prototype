from dataclasses import dataclass, field
from typing import List, Optional
from inference_engine.schemas import DiagnosticPhase, DiagnosticDifficulty


@dataclass
class DiagnosticInteraction:
    """A single interaction record within the diagnostic session."""
    interaction_num: int
    level: int
    difficulty: DiagnosticDifficulty
    resource_id: str
    correct: bool
    tra_ms: int
    is_timeout: bool


@dataclass
class DiagnosticState:
    """
    Full state of a diagnostic session, persisted in Redis.
    This is the core state machine — transitions are handled by the evaluator.

    Valid transitions:
        INITIALIZING   → AWAITING_BASAL  (first exercise selected)
        AWAITING_BASAL → EXPLORING       (basal established: 3 correct + TRA < 4s)
        AWAITING_BASAL → EXPLORING       (basal not established, keep testing)
        EXPLORING      → CEILING_DETECTED (3 consecutive errors/timeouts)
        EXPLORING      → LIMIT_REACHED   (interaction_num > 15)
        EXPLORING      → EXPLORING       (normal progression between levels)
        CEILING_DETECTED → COMPLETED     (result calculated and persisted)
        LIMIT_REACHED    → COMPLETED     (result calculated and persisted)
    """
    session_diag_id: str
    child_id: str
    phase: DiagnosticPhase = DiagnosticPhase.INITIALIZING
    interaction_num: int = 0
    current_test_level: int = 1
    current_difficulty: DiagnosticDifficulty = DiagnosticDifficulty.LOW
    basal_established: bool = False
    basal_level: Optional[int] = None
    ceiling_detected: bool = False
    ceiling_level: Optional[int] = None
    consecutive_correct: int = 0
    consecutive_errors: int = 0
    used_items: List[str] = field(default_factory=list)
    history: List[DiagnosticInteraction] = field(default_factory=list)
