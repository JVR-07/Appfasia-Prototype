import pytest
import pytest_asyncio

from inference_engine.graph.schemas import HitoNode, HitoDimension, LagTicket
from inference_engine.graph.navigator import GraphNavigator, NetworkXBackend
from inference_engine.graph.lag_detector import LagDetector


# Fixtures
def _make_hito(
    id_hito: str,
    nivel: int = 1,
    orden: int = 1,
    bloqueante: bool = False,
    dimension: HitoDimension = HitoDimension.EXPRESIVO,
) -> HitoNode:
    return HitoNode(
        id_hito=id_hito,
        nombre=f"Test hito {id_hito}",
        nivel=nivel,
        rango_edad_min=nivel * 12,
        rango_edad_max=(nivel + 1) * 12,
        dimension=dimension,
        es_bloqueante=bloqueante,
        orden_interno=orden,
    )


@pytest_asyncio.fixture
async def three_level_graph():
    """
    3-level graph for lag detection:
      Level 1: L1_A(bloq) -> L1_B(bloq)
      Level 2: L2_A(bloq) -> L2_B
      Level 3: L3_A -> L3_B
      Cross: L1_B -> L2_A, L2_A -> L3_A
    """
    backend = NetworkXBackend()

    l1a = _make_hito("L1_A", nivel=1, orden=1, bloqueante=True)
    l1b = _make_hito("L1_B", nivel=1, orden=2, bloqueante=True)
    l2a = _make_hito("L2_A", nivel=2, orden=1, bloqueante=True)
    l2b = _make_hito("L2_B", nivel=2, orden=2, bloqueante=False)
    l3a = _make_hito("L3_A", nivel=3, orden=1, bloqueante=False)
    l3b = _make_hito("L3_B", nivel=3, orden=2, bloqueante=False)

    for h in [l1a, l1b, l2a, l2b, l3a, l3b]:
        backend.add_hito(h)

    backend.add_dependency("L1_A", "L1_B")
    backend.add_dependency("L1_B", "L2_A")
    backend.add_dependency("L2_A", "L2_B")
    backend.add_dependency("L2_A", "L3_A")
    backend.add_dependency("L3_A", "L3_B")

    nav = GraphNavigator(backend)
    detector = LagDetector(nav)
    yield detector, nav
    await nav.close()


@pytest_asyncio.fixture
async def five_level_graph():
    """
    5-level graph for deeper lag detection:
      Each level has one bloqueante hito chained to the next level.
    """
    backend = NetworkXBackend()
    prev_id = None

    for level in range(1, 6):
        h = _make_hito(
            f"L{level}",
            nivel=level,
            orden=1,
            bloqueante=True,
        )
        backend.add_hito(h)
        if prev_id:
            backend.add_dependency(prev_id, f"L{level}")
        prev_id = f"L{level}"

    nav = GraphNavigator(backend)
    detector = LagDetector(nav)
    yield detector, nav
    await nav.close()


# Tests: detect_lags
class TestDetectLags:
    @pytest.mark.asyncio
    async def test_no_lag_at_low_levels(self, three_level_graph):
        """At level 1 or 2, no lags can exist (distance < 2)."""
        detector, _ = three_level_graph
        lags = await detector.detect_lags(set(), current_level=1)
        assert lags == []

        lags = await detector.detect_lags(set(), current_level=2)
        assert lags == []

    @pytest.mark.asyncio
    async def test_detects_level1_gap_at_level3(self, three_level_graph):
        """At level 3, unmastered bloqueante hitos at level 1 are detected."""
        detector, _ = three_level_graph
        # Child is at level 3 but hasn't mastered level 1
        mastered = {"L2_A", "L3_A"}
        lags = await detector.detect_lags(mastered, current_level=3)

        assert len(lags) >= 1
        lag_ids = [t.lag_hito_id for t in lags]
        assert "L1_A" in lag_ids or "L1_B" in lag_ids

    @pytest.mark.asyncio
    async def test_no_lag_when_all_mastered(self, three_level_graph):
        """No lags when all hitos are mastered."""
        detector, _ = three_level_graph
        mastered = {"L1_A", "L1_B", "L2_A", "L2_B", "L3_A", "L3_B"}
        lags = await detector.detect_lags(mastered, current_level=3)
        assert lags == []

    @pytest.mark.asyncio
    async def test_ignores_non_bloqueante(self, three_level_graph):
        """Non-bloqueante hitos at lag levels are ignored."""
        detector, _ = three_level_graph
        # L2_B is not bloqueante, so even if unmastered it's not a lag
        # L3_A and L3_B are level 3 so never a lag at level 3
        mastered = {"L1_A", "L1_B", "L2_A"}
        lags = await detector.detect_lags(mastered, current_level=3)
        # L2_B is level 2, threshold is 1, so level 2 is not <= 1
        assert lags == []

    @pytest.mark.asyncio
    async def test_lag_ticket_structure(self, three_level_graph):
        """Verify the LagTicket has correct fields."""
        detector, _ = three_level_graph
        mastered = {"L2_A", "L3_A"}
        lags = await detector.detect_lags(mastered, current_level=3)

        for lag in lags:
            assert isinstance(lag, LagTicket)
            assert lag.child_level == 3
            assert lag.lag_level <= 1
            assert isinstance(lag.recovery_hitos, list)

    @pytest.mark.asyncio
    async def test_sorted_by_level_ascending(self, five_level_graph):
        """Lags should be sorted by lag_level ascending (deepest first)."""
        detector, _ = five_level_graph
        # At level 5, everything below level 3 is a potential lag
        mastered = {"L4", "L5"}
        lags = await detector.detect_lags(mastered, current_level=5)

        levels = [t.lag_level for t in lags]
        assert levels == sorted(levels)

    @pytest.mark.asyncio
    async def test_deeper_lag_detection_level5(self, five_level_graph):
        """At level 5, lags at levels 1, 2, and 3 are detected."""
        detector, _ = five_level_graph
        mastered = {"L4", "L5"}
        lags = await detector.detect_lags(mastered, current_level=5)

        lag_ids = {t.lag_hito_id for t in lags}
        assert "L1" in lag_ids
        assert "L2" in lag_ids
        assert "L3" in lag_ids

    @pytest.mark.asyncio
    async def test_recovery_route_populated(self, five_level_graph):
        """Each lag ticket should have a non-empty recovery route."""
        detector, _ = five_level_graph
        mastered = {"L4", "L5"}
        lags = await detector.detect_lags(mastered, current_level=5)

        for lag in lags:
            assert len(lag.recovery_hitos) >= 1



# Tests: get_micro_exercise_hitos
class TestGetMicroExerciseHitos:
    @pytest.mark.asyncio
    async def test_returns_up_to_max_count(self, three_level_graph):
        """Should return at most max_count hito IDs."""
        detector, _ = three_level_graph
        tickets = [
            LagTicket(
                child_level=3,
                lag_hito_id="L1_A",
                lag_level=1,
                recovery_hitos=["L1_A", "L1_B"],
            ),
            LagTicket(
                child_level=3,
                lag_hito_id="L1_B",
                lag_level=1,
                recovery_hitos=["L1_B"],
            ),
        ]
        result = await detector.get_micro_exercise_hitos(tickets, max_count=2)
        assert len(result) <= 2

    @pytest.mark.asyncio
    async def test_deduplicates(self, three_level_graph):
        """Should not return the same hito ID twice."""
        detector, _ = three_level_graph
        tickets = [
            LagTicket(
                child_level=3,
                lag_hito_id="L1_A",
                lag_level=1,
                recovery_hitos=["L1_A", "L1_B"],
            ),
            LagTicket(
                child_level=3,
                lag_hito_id="L1_B",
                lag_level=1,
                recovery_hitos=["L1_A", "L1_B"],  # overlapping
            ),
        ]
        result = await detector.get_micro_exercise_hitos(tickets, max_count=5)
        assert len(result) == len(set(result))  # no duplicates

    @pytest.mark.asyncio
    async def test_empty_tickets(self, three_level_graph):
        """Empty ticket list returns empty result."""
        detector, _ = three_level_graph
        result = await detector.get_micro_exercise_hitos([], max_count=2)
        assert result == []

    @pytest.mark.asyncio
    async def test_respects_max_count(self, three_level_graph):
        """With max_count=1, only one hito is returned."""
        detector, _ = three_level_graph
        tickets = [
            LagTicket(
                child_level=3,
                lag_hito_id="L1_A",
                lag_level=1,
                recovery_hitos=["L1_A", "L1_B", "L2_A"],
            ),
        ]
        result = await detector.get_micro_exercise_hitos(tickets, max_count=1)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_prioritizes_deepest_lag(self, three_level_graph):
        """Tickets sorted by lag_level, so deepest lag gets picked first."""
        detector, _ = three_level_graph
        tickets = [
            LagTicket(
                child_level=4,
                lag_hito_id="L1_A",
                lag_level=1,
                recovery_hitos=["DEEP_FIX"],
            ),
            LagTicket(
                child_level=4,
                lag_hito_id="L2_A",
                lag_level=2,
                recovery_hitos=["SHALLOW_FIX"],
            ),
        ]
        result = await detector.get_micro_exercise_hitos(tickets, max_count=1)
        assert result == ["DEEP_FIX"]
