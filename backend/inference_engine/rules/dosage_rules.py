from typing import Optional, Dict
from inference_engine.schemas import MinigameType
from inference_engine.rules.constants import (
    SESSION_LIMITS,
    MINIGAME_REWARD_STREAK,
    MINIGAME_RESCUE_STREAK
)


def check_session_limit(level: int, elapsed_minutes: float, exercises_done: int) -> bool:
    """Returns True if session should end (time or exercise cap reached)."""
    limits = SESSION_LIMITS.get(level, SESSION_LIMITS[1])

    if elapsed_minutes >= limits["max_minutes"]:
        return True

    if exercises_done >= limits["exercises"][1]:
        return True

    return False


def should_trigger_minigame(
    consecutive_correct: int,
    consecutive_errors: int
) -> Optional[MinigameType]:
    """
    Returns MinigameType.REWARD, MinigameType.RESCUE, or None.
    """
    if consecutive_correct >= MINIGAME_REWARD_STREAK:
        return MinigameType.REWARD

    if consecutive_errors >= MINIGAME_RESCUE_STREAK:
        return MinigameType.RESCUE

    return None


def get_session_structure(level: int) -> Dict[str, any]:
    """Returns max_minutes, exercises range, minigame count for this level."""
    return SESSION_LIMITS.get(level, SESSION_LIMITS[1])
