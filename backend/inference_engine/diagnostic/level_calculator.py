from datetime import date
from typing import Tuple
from inference_engine.schemas import DiagnosticDifficulty


def calculate_age_months(birth_date: date) -> int:
    """Returns the child's age in months."""
    today = date.today()
    return (today.year - birth_date.year) * 12 + (today.month - birth_date.month)


def expected_level(age_months: int) -> int:
    """Maps age in months to the expected competence level (1-5)."""
    if age_months < 24:
        return 1
    if age_months < 48:
        return 2
    if age_months < 72:
        return 3
    if age_months < 96:
        return 4
    return 5


def start_level(exp_level: int) -> Tuple[int, DiagnosticDifficulty]:
    """
    Returns (level, difficulty) to begin the diagnostic.
    Always starts half a level below the expected level to build confidence.
    """
    if exp_level == 1:
        return (1, DiagnosticDifficulty.LOW)
    return (exp_level - 1, DiagnosticDifficulty.HIGH)
