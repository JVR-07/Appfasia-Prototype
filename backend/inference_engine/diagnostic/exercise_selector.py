from dataclasses import dataclass
from typing import List, Protocol
from inference_engine.schemas import DiagnosticDifficulty


@dataclass
class ActivityInstance:
    """A single diagnostic exercise ready to present to the child."""
    template: str
    hardware_req: str
    prompt_audio_url: str
    options: List[dict]
    correct_resource_id: str


class ExerciseRepository(Protocol):
    """
    Abstract interface for fetching diagnostic exercises.
    Implement with PostgreSQL for production, or with a dict for tests.
    """

    async def fetch_resource(
        self,
        level: int,
        difficulty: DiagnosticDifficulty,
        exclude_ids: List[str]
    ) -> dict:
        """Returns a single resource matching level/difficulty, excluding used items."""
        ...

    async def fetch_distractors(
        self,
        level: int,
        correct_id: str,
        exclude_ids: List[str],
        count: int = 2
    ) -> List[dict]:
        """Returns N distractor resources at the same level."""
        ...


async def select_diagnostic_exercise(
    repo: ExerciseRepository,
    level: int,
    difficulty: DiagnosticDifficulty,
    used_items: List[str]
) -> ActivityInstance:
    """
    Selects a diagnostic exercise using the Identificador (T-S) template.
    Diagnostic always uses 3 visual options: 1 correct + 2 distractors.
    P(G) = 1/3 = 0.33
    """
    correct = await repo.fetch_resource(level, difficulty, used_items)
    distractors = await repo.fetch_distractors(
        level, correct["id_recurso"], used_items, count=2
    )

    all_options = [correct] + distractors

    return ActivityInstance(
        template="Identificador",
        hardware_req="T-S",
        prompt_audio_url=correct.get("audio_url", ""),
        options=all_options,
        correct_resource_id=correct["id_recurso"]
    )
