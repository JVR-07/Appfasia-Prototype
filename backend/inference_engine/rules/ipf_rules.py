from typing import Optional
from inference_engine.schemas import IPFRuleResult, IPFOutcome, AvatarMode
from inference_engine.rules.constants import (
    IPF_MASTERY,
    IPF_BLOCK,
    IPF_BLOCK_STREAK
)


def evaluate_ipf(
    ipf: Optional[float],
    is_low_confidence: bool,
    consecutive_low_ipf: int
) -> IPFRuleResult:
    """
    Evaluates the IPF metric and returns a typed result.

    Decision table:
      - No IPF data             → SKIP (no penalty)
      - STT confidence < 0.70   → LOW_CONFIDENCE (no penalty)
      - IPF >= 80               → MASTERED
      - IPF < 50 (x3 streak)   → HARDWARE_OVERRIDE (switch to T-S)
      - IPF < 50 (streak < 3)  → PRACTICE (with SUPPORT avatar)
      - 50 <= IPF < 80          → PRACTICE
    """
    if ipf is None:
        return IPFRuleResult(
            outcome=IPFOutcome.SKIP,
            trigger_override=False,
            avatar_mode=AvatarMode.NEUTRAL
        )

    if is_low_confidence:
        return IPFRuleResult(
            outcome=IPFOutcome.LOW_CONFIDENCE,
            trigger_override=False,
            avatar_mode=AvatarMode.NEUTRAL
        )

    if ipf >= IPF_MASTERY:
        return IPFRuleResult(
            outcome=IPFOutcome.MASTERED,
            trigger_override=False,
            avatar_mode=AvatarMode.CHALLENGE
        )

    if ipf < IPF_BLOCK and consecutive_low_ipf >= IPF_BLOCK_STREAK:
        return IPFRuleResult(
            outcome=IPFOutcome.HARDWARE_OVERRIDE,
            trigger_override=True,
            avatar_mode=AvatarMode.SUPPORT
        )

    return IPFRuleResult(
        outcome=IPFOutcome.PRACTICE,
        trigger_override=False,
        avatar_mode=AvatarMode.SUPPORT if ipf < IPF_BLOCK else AvatarMode.NEUTRAL
    )
