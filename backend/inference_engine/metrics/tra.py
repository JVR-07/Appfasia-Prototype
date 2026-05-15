from dataclasses import dataclass
from inference_engine.rules.constants import (
    TRA_FLUENCY_MS,
    TRA_HINT_MS,
    TRA_TIMEOUT_MS
)

@dataclass
class TRAResult:
    tra_ms: int
    is_timeout: bool
    is_hint_triggered: bool
    is_fluent: bool

def classify_tra(tra_ms: int) -> TRAResult:
    return TRAResult(
        tra_ms=tra_ms,
        is_timeout=tra_ms >= TRA_TIMEOUT_MS,
        is_hint_triggered=tra_ms >= TRA_HINT_MS,
        is_fluent=tra_ms <= TRA_FLUENCY_MS,
    )
