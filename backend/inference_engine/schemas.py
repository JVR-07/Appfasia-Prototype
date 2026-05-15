from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ──────────────────────────────────────────────
# Enums — Single source of truth for all states
# ──────────────────────────────────────────────

class EngineAction(str, Enum):
    """Actions the inference engine can take after evaluating a response."""
    ADVANCE = "ADVANCE"
    REPEAT = "REPEAT"
    MINIGAME = "MINIGAME"
    LEVEL_DOWN = "LEVEL_DOWN"
    HARDWARE_OVERRIDE = "HARDWARE_OVERRIDE"
    END_SESSION = "END_SESSION"


class MinigameType(str, Enum):
    """Types of minigame the engine can trigger."""
    REWARD = "REWARD"
    RESCUE = "RESCUE"


class HardwareMode(str, Enum):
    """Exercise hardware/interaction modes."""
    T_S = "T-S"
    T_A = "T-A"
    V_M = "V-M"


class AvatarMode(str, Enum):
    """Avatar communication modes based on the child's performance."""
    SUPPORT = "SUPPORT"
    CHALLENGE = "CHALLENGE"
    NEUTRAL = "NEUTRAL"


class IPFOutcome(str, Enum):
    """Possible outcomes from IPF rule evaluation."""
    MASTERED = "MASTERED"
    PRACTICE = "PRACTICE"
    HARDWARE_OVERRIDE = "HARDWARE_OVERRIDE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    SKIP = "SKIP"


class TRAOutcome(str, Enum):
    """Possible outcomes from TRA rule evaluation."""
    FLUENT = "FLUENT"
    DELAYED = "DELAYED"
    TIMEOUT = "TIMEOUT"
    VM_BLOCKED = "VM_BLOCKED"
    NORMAL = "NORMAL"


class LMEOutcome(str, Enum):
    """Possible outcomes from LME rule evaluation."""
    TELEGRAPHIC = "TELEGRAPHIC"
    TRANSITIONAL = "TRANSITIONAL"
    SYNTACTIC = "SYNTACTIC"
    VALID_ZERO = "VALID_ZERO"
    SKIP = "SKIP"


class DiagnosticPhase(str, Enum):
    """State machine phases for the diagnostic algorithm."""
    INITIALIZING = "INITIALIZING"
    AWAITING_BASAL = "AWAITING_BASAL"
    EXPLORING = "EXPLORING"
    CEILING_DETECTED = "CEILING_DETECTED"
    LIMIT_REACHED = "LIMIT_REACHED"
    COMPLETED = "COMPLETED"


class DiagnosticDifficulty(str, Enum):
    """Difficulty tiers within a single level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DiagnosticExitReason(str, Enum):
    """Why the diagnostic session ended."""
    CEILING = "CEILING"
    LIMIT_REACHED = "LIMIT_REACHED"


# ──────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────

@dataclass
class RawMetrics:
    """Raw metrics computed from a single user response."""
    ipf: Optional[float]
    lme: Optional[float]
    tra_ms: int
    is_timeout: bool
    is_low_confidence: bool


@dataclass
class BKTState:
    """Bayesian Knowledge Tracing state for a single milestone (hito)."""
    hito_id: str
    p_mastery: float
    p_transit: float = 0.20
    p_slip: float = 0.10
    p_guess: float = 0.25
    is_mastered: bool = False


@dataclass
class SessionContext:
    """Current session state needed for decision making."""
    level: int
    consecutive_correct: int
    consecutive_errors: int
    consecutive_timeouts: int
    exercises_done: int
    elapsed_minutes: float


@dataclass
class IPFRuleResult:
    """Structured result from IPF rule evaluation."""
    outcome: IPFOutcome
    trigger_override: bool
    avatar_mode: AvatarMode


@dataclass
class TRARuleResult:
    """Structured result from TRA rule evaluation."""
    outcome: TRAOutcome
    trigger_vm_block: bool


@dataclass
class LMERuleResult:
    """Structured result from LME rule evaluation."""
    outcome: LMEOutcome
    suggest_level: Optional[int]


@dataclass
class EngineDecision:
    """Final decision returned by the inference engine."""
    action: EngineAction
    minigame_type: Optional[MinigameType] = None
    hardware_override: Optional[HardwareMode] = None
    requires_graph_query: bool = False
    target_level: Optional[int] = None
    avatar_mode: AvatarMode = AvatarMode.NEUTRAL
    consecutive_correct: int = 0
    consecutive_errors: int = 0
