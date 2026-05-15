from typing import Optional
from inference_engine.schemas import LMERuleResult, LMEOutcome
from inference_engine.rules.constants import (
    LME_TELEGRAPHIC_LOW,
    LME_TELEGRAPHIC_HIGH,
    LME_SYNTACTIC,
    LME_ZERO_VALID
)


def evaluate_lme(lme: Optional[float], current_level: int) -> LMERuleResult:
    """
    Evaluates the LME metric and returns a typed result.

    Decision table:
      - No LME data                         → SKIP
      - LME == 0 at Level 1-2               → VALID_ZERO (clinically expected)
      - 2 <= LME <= 4                        → TELEGRAPHIC (suggest Level 2)
      - LME > 4                              → SYNTACTIC (suggest Level 3)
      - LME < 2 (non-zero, Level 3+)        → TRANSITIONAL
    """
    if lme is None:
        return LMERuleResult(outcome=LMEOutcome.SKIP, suggest_level=None)

    if lme == 0 and current_level in (1, 2) and LME_ZERO_VALID:
        return LMERuleResult(outcome=LMEOutcome.VALID_ZERO, suggest_level=None)

    if LME_TELEGRAPHIC_LOW <= lme <= LME_TELEGRAPHIC_HIGH:
        return LMERuleResult(outcome=LMEOutcome.TELEGRAPHIC, suggest_level=2)

    if lme > LME_SYNTACTIC:
        return LMERuleResult(outcome=LMEOutcome.SYNTACTIC, suggest_level=3)

    return LMERuleResult(outcome=LMEOutcome.TRANSITIONAL, suggest_level=None)
