"""
Knowledge-graph navigator for the pedagogical hito graph.

Provides an abstraction over graph queries, supporting both:
  - ArcadeDB via BOLT protocol (production) using the neo4j async driver
  - NetworkX in-memory graphs (unit testing, offline operation)

The navigator never mutates the graph; it is read-only.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from inference_engine.graph.schemas import EdgeType, HitoNode

# Abstract interface
@runtime_checkable
class GraphBackend(Protocol):
    """Pluggable backend so we can swap ArcadeDB for NetworkX in tests."""

    async def get_all_hitos(self) -> list[HitoNode]:
        ...

    async def get_prerequisites(self, hito_id: str) -> list[str]:
        ...

    async def get_dependents(self, hito_id: str) -> list[str]:
        ...

    async def get_hito(self, hito_id: str) -> HitoNode | None:
        ...

    async def get_alternative(self, hito_id: str) -> str | None:
        ...

    async def close(self) -> None:
        ...

# NetworkX backend (testing & offline)
try:
    import networkx as nx
except ImportError:
    nx = None


class NetworkXBackend:
    def __init__(self) -> None:
        if nx is None:
            raise ImportError("networkx is required for NetworkXBackend")
        self._g: nx.DiGraph = nx.DiGraph()
        self._hitos: dict[str, HitoNode] = {}

    # ── Graph construction helpers ──

    def add_hito(self, hito: HitoNode) -> None:
        self._hitos[hito.id_hito] = hito
        self._g.add_node(hito.id_hito)

    def add_dependency(self, prereq_id: str, dependent_id: str) -> None:
        self._g.add_edge(prereq_id, dependent_id, type=EdgeType.REQUIERE_DE)

    def add_alternative(self, blocked_id: str, alt_id: str) -> None:
        self._g.add_edge(blocked_id, alt_id, type=EdgeType.RUTA_ALTERNATIVA)

    # ── Protocol implementation ──

    async def get_all_hitos(self) -> list[HitoNode]:
        return list(self._hitos.values())

    async def get_prerequisites(self, hito_id: str) -> list[str]:
        return [
            src
            for src, dst, data in self._g.in_edges(hito_id, data=True)
            if data.get("type") == EdgeType.REQUIERE_DE
        ]

    async def get_dependents(self, hito_id: str) -> list[str]:
        return [
            dst
            for src, dst, data in self._g.out_edges(hito_id, data=True)
            if data.get("type") == EdgeType.REQUIERE_DE
        ]

    async def get_hito(self, hito_id: str) -> HitoNode | None:
        return self._hitos.get(hito_id)

    async def get_alternative(self, hito_id: str) -> str | None:
        for _, dst, data in self._g.out_edges(hito_id, data=True):
            if data.get("type") == EdgeType.RUTA_ALTERNATIVA:
                return dst
        return None

    async def close(self) -> None:
        pass

# ArcadeDB BOLT backend (production)
class ArcadeDBBackend:
    def __init__(
        self, bolt_uri: str, user: str, password: str, database: str
    ) -> None:
        from neo4j import AsyncGraphDatabase
        self._driver = AsyncGraphDatabase.driver(
            bolt_uri, auth=(user, password)
        )
        self._db = database

    async def get_all_hitos(self) -> list[HitoNode]:
        query = "MATCH (h:Hito) RETURN h ORDER BY h.nivel, h.orden_interno"
        async with self._driver.session(database=self._db) as session:
            result = await session.run(query)
            records = await result.data()
        return [self._record_to_hito(r["h"]) for r in records]

    async def get_prerequisites(self, hito_id: str) -> list[str]:
        query = (
            "MATCH (prereq:Hito)-[:REQUIERE_DE]->(h:Hito {id_hito: $hito_id}) "
            "RETURN prereq.id_hito AS id"
        )
        async with self._driver.session(database=self._db) as session:
            result = await session.run(query, hito_id=hito_id)
            records = await result.data()
        return [r["id"] for r in records]

    async def get_dependents(self, hito_id: str) -> list[str]:
        query = (
            "MATCH (h:Hito {id_hito: $hito_id})-[:REQUIERE_DE]->(dep:Hito) "
            "RETURN dep.id_hito AS id"
        )
        async with self._driver.session(database=self._db) as session:
            result = await session.run(query, hito_id=hito_id)
            records = await result.data()
        return [r["id"] for r in records]

    async def get_hito(self, hito_id: str) -> HitoNode | None:
        query = "MATCH (h:Hito {id_hito: $hito_id}) RETURN h"
        async with self._driver.session(database=self._db) as session:
            result = await session.run(query, hito_id=hito_id)
            record = await result.single()
        if record is None:
            return None
        return self._record_to_hito(record["h"])

    async def get_alternative(self, hito_id: str) -> str | None:
        query = (
            "MATCH (h:Hito {id_hito: $hito_id})-[:RUTA_ALTERNATIVA]->(alt:Hito) "
            "RETURN alt.id_hito AS id LIMIT 1"
        )
        async with self._driver.session(database=self._db) as session:
            result = await session.run(query, hito_id=hito_id)
            record = await result.single()
        return record["id"] if record else None

    async def close(self) -> None:
        await self._driver.close()

    @staticmethod
    def _record_to_hito(props: dict) -> HitoNode:
        return HitoNode(
            id_hito=props["id_hito"],
            nombre=props["nombre"],
            nivel=props["nivel"],
            rango_edad_min=props["rango_edad_min"],
            rango_edad_max=props["rango_edad_max"],
            dimension=props["dimension"],
            es_bloqueante=props["es_bloqueante"],
            orden_interno=props["orden_interno"],
        )

# GraphNavigator — main public API
class GraphNavigator:
    def __init__(self, backend: GraphBackend) -> None:
        self._backend = backend

    async def close(self) -> None:
        await self._backend.close()

    async def get_next_optimal_hito(
        self, mastered_ids: set[str], current_level: int
    ) -> HitoNode | None:
        """Return the next unmastered hito whose prerequisites are all met.

        Selection priority:
          1. Same level as current_level, lowest orden_interno
          2. Next level (current_level + 1)
        Returns None if all hitos are mastered.
        """
        all_hitos = await self._backend.get_all_hitos()
        candidates = [
            h for h in all_hitos
            if h.id_hito not in mastered_ids and h.nivel >= current_level
        ]
        candidates.sort(key=lambda h: (h.nivel, h.orden_interno))

        for candidate in candidates:
            prereqs = await self._backend.get_prerequisites(candidate.id_hito)
            if all(p in mastered_ids for p in prereqs):
                return candidate
        return None

    async def get_blocking_hitos(
        self, target_hito_id: str, mastered_ids: set[str]
    ) -> list[str]:
        prereqs = await self._backend.get_prerequisites(target_hito_id)
        return [p for p in prereqs if p not in mastered_ids]

    async def get_recovery_route(
        self, lag_hito_id: str, mastered_ids: set[str]
    ) -> list[str]:
        """Return an ordered path from the lag hito to the nearest mastered ancestor.

        Traverses REQUIERE_DE edges upward from the lag hito, collecting
        unmastered ancestors, and returns them in bottom-up order (the lag
        hito first, its unmastered prereqs next, etc.) until a mastered
        ancestor or a root node is reached.
        """
        route: list[str] = []
        visited: set[str] = set()
        queue = [lag_hito_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            if current not in mastered_ids:
                route.append(current)
                prereqs = await self._backend.get_prerequisites(current)
                for p in prereqs:
                    if p not in visited:
                        queue.append(p)
            # Stop traversal once we reach mastered territory

        # Reverse so the deepest unmastered ancestor comes first
        route.reverse()
        return route

    async def get_available_hitos(
        self, mastered_ids: set[str], level: int
    ) -> list[HitoNode]:
        all_hitos = await self._backend.get_all_hitos()
        available: list[HitoNode] = []

        for h in all_hitos:
            if h.nivel != level or h.id_hito in mastered_ids:
                continue
            prereqs = await self._backend.get_prerequisites(h.id_hito)
            if all(p in mastered_ids for p in prereqs):
                available.append(h)

        available.sort(key=lambda h: h.orden_interno)
        return available

    async def get_hitos_by_level(self, level: int) -> list[HitoNode]:
        all_hitos = await self._backend.get_all_hitos()
        level_hitos = [h for h in all_hitos if h.nivel == level]
        level_hitos.sort(key=lambda h: h.orden_interno)
        return level_hitos

    async def get_route(
        self, mastered_ids: set[str], current_level: int
    ) -> GraphRoute | None:
        """Build a full GraphRoute for the current state.

        Combines get_next_optimal_hito, get_blocking_hitos, and
        alternative route lookup into a single convenient result.
        """
        from inference_engine.graph.schemas import GraphRoute

        next_hito = await self.get_next_optimal_hito(
            mastered_ids, current_level
        )
        if next_hito is None:
            return None

        blocked_by = await self.get_blocking_hitos(
            next_hito.id_hito, mastered_ids
        )
        alternative = await self._backend.get_alternative(next_hito.id_hito)

        return GraphRoute(
            next_hito=next_hito,
            blocked_by=blocked_by,
            alternative_route=alternative,
        )
