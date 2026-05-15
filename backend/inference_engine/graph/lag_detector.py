from __future__ import annotations

from inference_engine.graph.navigator import GraphNavigator
from inference_engine.graph.schemas import LagTicket


class LagDetector:
    LAG_LEVEL_DISTANCE = 2

    def __init__(self, navigator: GraphNavigator) -> None:
        self._nav = navigator

    async def detect_lags(
        self, mastered_ids: set[str], current_level: int
    ) -> list[LagTicket]:
        """Scan for foundational gaps at level <= current_level - 2.

        A hito qualifies as a lag if:
          1. It is at level <= current_level - LAG_LEVEL_DISTANCE
          2. It is NOT mastered
          3. It is marked as bloqueante (foundational)

        Returns a list of LagTickets sorted by level (lowest first),
        each containing a recovery route from the lag hito back to
        the nearest mastered ancestor.
        """
        if current_level <= self.LAG_LEVEL_DISTANCE:
            return []  # No lag possible at levels 1-2

        lag_threshold = current_level - self.LAG_LEVEL_DISTANCE
        tickets: list[LagTicket] = []

        for level in range(1, lag_threshold + 1):
            hitos_at_level = await self._nav.get_hitos_by_level(level)

            for hito in hitos_at_level:
                if hito.id_hito in mastered_ids:
                    continue
                if not hito.es_bloqueante:
                    continue  # Only flag foundational gaps

                recovery = await self._nav.get_recovery_route(
                    hito.id_hito, mastered_ids
                )

                tickets.append(
                    LagTicket(
                        child_level=current_level,
                        lag_hito_id=hito.id_hito,
                        lag_level=hito.nivel,
                        recovery_hitos=recovery,
                    )
                )

        tickets.sort(key=lambda t: t.lag_level)
        return tickets

    async def get_micro_exercise_hitos(
        self, lag_tickets: list[LagTicket], max_count: int = 2
    ) -> list[str]:
        """Pick up to ``max_count`` hito IDs from lag tickets to inject
        as disguised micro-exercises in the current session.

        Selection strategy:
          1. Prioritize the deepest lag (lowest level first)
          2. From each ticket, pick the first recovery hito that
             has its own prerequisites met (i.e., is actionable)
          3. Deduplicate across tickets
        """
        selected: list[str] = []
        seen: set[str] = set()

        for ticket in lag_tickets:
            if len(selected) >= max_count:
                break

            for hito_id in ticket.recovery_hitos:
                if hito_id in seen:
                    continue
                seen.add(hito_id)
                selected.append(hito_id)
                if len(selected) >= max_count:
                    break

        return selected
