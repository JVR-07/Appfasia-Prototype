import pytest
import pytest_asyncio

from inference_engine.graph.schemas import HitoNode, HitoDimension, GraphRoute
from inference_engine.graph.navigator import (
    GraphNavigator,
    NetworkXBackend,
)

# Fixtures — reusable mini-graph
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
        rango_edad_min=0,
        rango_edad_max=12,
        dimension=dimension,
        es_bloqueante=bloqueante,
        orden_interno=orden,
    )


@pytest_asyncio.fixture
async def linear_graph():
    """Simple linear graph: A -> B -> C (all level 1)."""
    backend = NetworkXBackend()
    a = _make_hito("A", nivel=1, orden=1, bloqueante=True)
    b = _make_hito("B", nivel=1, orden=2)
    c = _make_hito("C", nivel=1, orden=3)
    backend.add_hito(a)
    backend.add_hito(b)
    backend.add_hito(c)
    backend.add_dependency("A", "B")
    backend.add_dependency("B", "C")
    nav = GraphNavigator(backend)
    yield nav
    await nav.close()


@pytest_asyncio.fixture
async def multi_level_graph():
    """
    Multi-level graph:
      Level 1: A(1) -> B(2)
      Level 2: C(1) -> D(2)
      Cross-level: B -> C (level 1 feeds level 2)
    """
    backend = NetworkXBackend()
    a = _make_hito("A", nivel=1, orden=1, bloqueante=True)
    b = _make_hito("B", nivel=1, orden=2, bloqueante=True)
    c = _make_hito("C", nivel=2, orden=1)
    d = _make_hito("D", nivel=2, orden=2)
    backend.add_hito(a)
    backend.add_hito(b)
    backend.add_hito(c)
    backend.add_hito(d)
    backend.add_dependency("A", "B")
    backend.add_dependency("B", "C")
    backend.add_dependency("C", "D")
    nav = GraphNavigator(backend)
    yield nav
    await nav.close()


@pytest_asyncio.fixture
async def branching_graph():
    """
    Branching graph with alternative route:
      A -> B -> D
      A -> C -> D
      B has RUTA_ALTERNATIVA -> C
    """
    backend = NetworkXBackend()
    a = _make_hito("A", nivel=1, orden=1, bloqueante=True)
    b = _make_hito("B", nivel=1, orden=2, bloqueante=True)
    c = _make_hito("C", nivel=1, orden=3)
    d = _make_hito("D", nivel=1, orden=4)
    backend.add_hito(a)
    backend.add_hito(b)
    backend.add_hito(c)
    backend.add_hito(d)
    backend.add_dependency("A", "B")
    backend.add_dependency("A", "C")
    backend.add_dependency("B", "D")
    backend.add_dependency("C", "D")
    backend.add_alternative("B", "C")
    nav = GraphNavigator(backend)
    yield nav
    await nav.close()


# Tests: get_next_optimal_hito
class TestGetNextOptimalHito:
    @pytest.mark.asyncio
    async def test_returns_root_when_nothing_mastered(self, linear_graph):
        """With no mastery, the root node (no prerequisites) is returned."""
        result = await linear_graph.get_next_optimal_hito(set(), 1)
        assert result is not None
        assert result.id_hito == "A"

    @pytest.mark.asyncio
    async def test_returns_next_after_mastering_root(self, linear_graph):
        """After mastering A, B becomes available."""
        result = await linear_graph.get_next_optimal_hito({"A"}, 1)
        assert result is not None
        assert result.id_hito == "B"

    @pytest.mark.asyncio
    async def test_returns_none_when_all_mastered(self, linear_graph):
        """When all hitos are mastered, returns None."""
        result = await linear_graph.get_next_optimal_hito(
            {"A", "B", "C"}, 1
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_skips_blocked_hito(self, linear_graph):
        """If B's prereq (A) isn't mastered, B is skipped."""
        # Only C has no prereq path satisfied without A
        result = await linear_graph.get_next_optimal_hito(set(), 1)
        assert result.id_hito == "A"  # A is the only available one

    @pytest.mark.asyncio
    async def test_cross_level_progression(self, multi_level_graph):
        """After mastering level 1, level 2 hitos become available."""
        mastered = {"A", "B"}
        result = await multi_level_graph.get_next_optimal_hito(mastered, 2)
        assert result is not None
        assert result.id_hito == "C"
        assert result.nivel == 2

    @pytest.mark.asyncio
    async def test_respects_level_filter(self, multi_level_graph):
        """When current_level=2, level 1 hitos are not returned."""
        result = await multi_level_graph.get_next_optimal_hito(set(), 2)
        # C requires B which requires A — nothing at level 2 is available
        assert result is None

    @pytest.mark.asyncio
    async def test_prefers_lower_orden_interno(self, multi_level_graph):
        """Within a level, the hito with the lowest orden_interno wins."""
        result = await multi_level_graph.get_next_optimal_hito(set(), 1)
        assert result.id_hito == "A"
        assert result.orden_interno == 1

# Tests: get_blocking_hitos
class TestGetBlockingHitos:
    @pytest.mark.asyncio
    async def test_returns_unmastered_prereqs(self, linear_graph):
        result = await linear_graph.get_blocking_hitos("B", set())
        assert result == ["A"]

    @pytest.mark.asyncio
    async def test_returns_empty_when_all_met(self, linear_graph):
        result = await linear_graph.get_blocking_hitos("B", {"A"})
        assert result == []

    @pytest.mark.asyncio
    async def test_root_has_no_blockers(self, linear_graph):
        result = await linear_graph.get_blocking_hitos("A", set())
        assert result == []

    @pytest.mark.asyncio
    async def test_multiple_blockers(self, branching_graph):
        """D depends on both B and C."""
        result = await branching_graph.get_blocking_hitos("D", {"A"})
        assert set(result) == {"B", "C"}

# Tests: get_recovery_route
class TestGetRecoveryRoute:
    @pytest.mark.asyncio
    async def test_single_step_recovery(self, linear_graph):
        """B is unmastered but A is mastered: route = [B]"""
        route = await linear_graph.get_recovery_route("B", {"A"})
        assert route == ["B"]

    @pytest.mark.asyncio
    async def test_multi_step_recovery(self, linear_graph):
        """C is the lag, nothing mastered: route = [A, B, C]"""
        route = await linear_graph.get_recovery_route("C", set())
        assert route == ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_partial_mastery(self, linear_graph):
        """C is lag, A is mastered: route = [B, C]"""
        route = await linear_graph.get_recovery_route("C", {"A"})
        assert route == ["B", "C"]

    @pytest.mark.asyncio
    async def test_already_mastered(self, linear_graph):
        """If the lag hito is already mastered, empty route."""
        route = await linear_graph.get_recovery_route("A", {"A"})
        assert route == []


# Tests: get_available_hitos
class TestGetAvailableHitos:
    @pytest.mark.asyncio
    async def test_returns_only_available(self, multi_level_graph):
        available = await multi_level_graph.get_available_hitos(set(), 1)
        ids = [h.id_hito for h in available]
        assert "A" in ids
        assert "B" not in ids  # B requires A

    @pytest.mark.asyncio
    async def test_all_become_available_after_mastery(
        self, multi_level_graph
    ):
        available = await multi_level_graph.get_available_hitos({"A"}, 1)
        ids = [h.id_hito for h in available]
        assert ids == ["B"]

    @pytest.mark.asyncio
    async def test_wrong_level_returns_empty(self, multi_level_graph):
        available = await multi_level_graph.get_available_hitos(set(), 3)
        assert available == []


# Tests: get_hitos_by_level
class TestGetHitosByLevel:
    @pytest.mark.asyncio
    async def test_returns_correct_level(self, multi_level_graph):
        hitos = await multi_level_graph.get_hitos_by_level(1)
        assert len(hitos) == 2
        assert all(h.nivel == 1 for h in hitos)

    @pytest.mark.asyncio
    async def test_ordered_by_orden_interno(self, multi_level_graph):
        hitos = await multi_level_graph.get_hitos_by_level(1)
        orders = [h.orden_interno for h in hitos]
        assert orders == sorted(orders)

    @pytest.mark.asyncio
    async def test_empty_level(self, multi_level_graph):
        hitos = await multi_level_graph.get_hitos_by_level(5)
        assert hitos == []


# Tests: get_route (combined)
class TestGetRoute:
    @pytest.mark.asyncio
    async def test_returns_graphroute(self, linear_graph):
        route = await linear_graph.get_route(set(), 1)
        assert isinstance(route, GraphRoute)
        assert route.next_hito.id_hito == "A"
        assert route.blocked_by == []

    @pytest.mark.asyncio
    async def test_includes_blockers(self, linear_graph):
        # Force querying from level 1 with nothing mastered
        route = await linear_graph.get_route(set(), 1)
        # A has no blockers
        assert route.blocked_by == []

    @pytest.mark.asyncio
    async def test_returns_none_when_all_done(self, linear_graph):
        route = await linear_graph.get_route({"A", "B", "C"}, 1)
        assert route is None

    @pytest.mark.asyncio
    async def test_includes_alternative_route(self, branching_graph):
        """B has RUTA_ALTERNATIVA -> C."""
        # Master A, then the next optimal is B (orden 2)
        route = await branching_graph.get_route({"A"}, 1)
        assert route.next_hito.id_hito == "B"
        assert route.alternative_route == "C"

# Tests: NetworkXBackend edge cases
class TestNetworkXBackend:
    @pytest.mark.asyncio
    async def test_get_hito_nonexistent(self):
        backend = NetworkXBackend()
        result = await backend.get_hito("NONEXISTENT")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_alternative_none(self):
        backend = NetworkXBackend()
        backend.add_hito(_make_hito("X"))
        result = await backend.get_alternative("X")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_prerequisites_empty(self):
        backend = NetworkXBackend()
        backend.add_hito(_make_hito("X"))
        result = await backend.get_prerequisites("X")
        assert result == []
