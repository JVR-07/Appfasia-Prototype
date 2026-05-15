from typing import Optional, List
from inference_engine.rules.constants import (
    EMA_WEIGHT_R0,
    EMA_WEIGHT_R1,
    EMA_WEIGHT_R2,
    LEVEL_DOWN_SESSIONS,
    IPF_PRACTICE_LOW
)

def compute_ema(r0: float, r1: Optional[float], r2: Optional[float]) -> float:
    """
    Computes Exponential Moving Average of session performance.
    """
    if r1 is None and r2 is None:
        return r0
        
    if r2 is None:
        total_weight = EMA_WEIGHT_R0 + EMA_WEIGHT_R1
        w0 = EMA_WEIGHT_R0 / total_weight
        w1 = EMA_WEIGHT_R1 / total_weight
        return (r0 * w0) + (r1 * w1)
        
    return (r0 * EMA_WEIGHT_R0) + (r1 * EMA_WEIGHT_R1) + (r2 * EMA_WEIGHT_R2)

def should_level_down(recent_emas: List[float]) -> bool:
    """
    Returns True if the last LEVEL_DOWN_SESSIONS EMA values are all below IPF_PRACTICE_LOW.
    Requires exactly LEVEL_DOWN_SESSIONS sessions of data.
    """
    if len(recent_emas) < LEVEL_DOWN_SESSIONS:
        return False
        
    last_n = recent_emas[-LEVEL_DOWN_SESSIONS:]
    return all(ema < IPF_PRACTICE_LOW for ema in last_n)
