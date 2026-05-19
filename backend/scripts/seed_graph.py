"""
Populates ArcadeDB with the complete hito catalog.

Can also be run with --dry-run to validate data without connecting.
"""

import os
import sys
import argparse

from hito_catalog import HITOS


def build_hito_dicts() -> tuple[list[dict], list[tuple[str, str]]]:
    """Parse HITOS tuples into node dicts and dependency edges."""
    nodes = []
    edges = []

    for i, entry in enumerate(HITOS):
        hid, nombre, nivel, emin, emax, dim, bloq, deps = entry
        nodes.append({
            "id_hito": hid,
            "nombre": nombre,
            "nivel": nivel,
            "rango_edad_min": emin,
            "rango_edad_max": emax,
            "dimension": dim,
            "es_bloqueante": bloq,
            "orden_interno": i + 1,
        })
        for dep in deps:
            edges.append((dep, hid))  # dep REQUIERE_DE -> hid

    return nodes, edges


def validate_catalog(nodes: list[dict], edges: list[tuple[str, str]]) -> bool:
    """Validate referential integrity of the catalog."""
    all_ids = {n["id_hito"] for n in nodes}
    ok = True

    for prereq, dependent in edges:
        if prereq not in all_ids:
            print(f"  ERROR: {dependent} depends on {prereq} which doesn't exist")
            ok = False
        if dependent not in all_ids:
            print(f"  ERROR: edge target {dependent} doesn't exist")
            ok = False

    dupes = [hid for hid in all_ids if sum(1 for n in nodes if n["id_hito"] == hid) > 1]
    if dupes:
        print(f"  ERROR: duplicate IDs: {dupes}")
        ok = False

    return ok


def print_summary(nodes: list[dict], edges: list[tuple[str, str]]) -> None:
    """Print a summary report."""
    by_level = {}
    for n in nodes:
        by_level.setdefault(n["nivel"], []).append(n)

    print("\n── Seed Summary ──")
    print(f"  Total hitos: {len(nodes)}")
    print(f"  Total REQUIERE_DE edges: {len(edges)}")
    bloq = sum(1 for n in nodes if n["es_bloqueante"])
    print(f"  Bloqueantes: {bloq}")
    for level in sorted(by_level):
        count = len(by_level[level])
        print(f"  Nivel {level}: {count} hitos")
    print()


async def seed_arcadedb(bolt_uri: str, user: str, password: str, db: str) -> None:
    """Connect to ArcadeDB and insert all hitos and edges."""
    import httpx
    from neo4j import AsyncGraphDatabase

    nodes, edges = build_hito_dicts()

    host = "arcadedb"
    if "://" in bolt_uri:
        parts = bolt_uri.split("://")[1].split(":")[0]
        if parts:
            host = parts

    http_url = f"http://{host}:2480"
    print(f"Ensuring database '{db}' exists at {http_url}...")
    try:
        with httpx.Client(base_url=http_url, auth=(user, password), timeout=30.0) as client:
            res = client.post("/api/v1/server", json={"command": f"create database {db}"})
            if res.status_code == 200:
                print(f"Database '{db}' created or already existed.")
            else:
                print(f"Database status response: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Warning: Could not check/create database via HTTP: {e}")

    print(f"Connecting to {bolt_uri}...")
    driver = AsyncGraphDatabase.driver(bolt_uri, auth=(user, password))

    try:
        async with driver.session(database=db) as session:
            # Create schema (handled dynamically by Cypher on node creation)
            # print("Creating vertex type Hito...")
            # await session.run(
            #     "CREATE VERTEX TYPE Hito IF NOT EXISTS"
            # )

            # Clear existing graph to make it idempotent
            print("Clearing existing graph...")
            await session.run("MATCH (n) DETACH DELETE n")

            # Insert nodes
            print(f"Inserting {len(nodes)} hitos...")
            for node in nodes:
                await session.run(
                    """
                    CREATE (h:Hito {
                        id_hito: $id_hito,
                        nombre: $nombre,
                        nivel: $nivel,
                        rango_edad_min: $rango_edad_min,
                        rango_edad_max: $rango_edad_max,
                        dimension: $dimension,
                        es_bloqueante: $es_bloqueante,
                        orden_interno: $orden_interno
                    })
                    """,
                    **node,
                )

            # Insert edges
            print(f"Inserting {len(edges)} REQUIERE_DE edges...")
            for prereq_id, dep_id in edges:
                await session.run(
                    """
                    MATCH (a:Hito {id_hito: $prereq}), (b:Hito {id_hito: $dep})
                    CREATE (a)-[:REQUIERE_DE {peso: 1.0}]->(b)
                    """,
                    prereq=prereq_id,
                    dep=dep_id,
                )

        print_summary(nodes, edges)
        print("Seed complete.")
    finally:
        await driver.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed ArcadeDB with hito catalog")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't connect")
    parser.add_argument("--bolt", default=os.getenv("ARCADE_BOLT", "bolt://arcadedb:7687"))
    parser.add_argument("--user", default=os.getenv("ARCADE_USER", "root"))
    parser.add_argument("--password", default=os.getenv("ARCADE_PASSWORD", "playrootpassword"))
    parser.add_argument("--database", default=os.getenv("ARCADE_DB", "appfasia"))
    args = parser.parse_args()

    nodes, edges = build_hito_dicts()

    print("Validating catalog...")
    if not validate_catalog(nodes, edges):
        print("Validation FAILED. Fix errors above.")
        sys.exit(1)
    print("Validation passed.")

    print_summary(nodes, edges)

    if args.dry_run:
        print("Dry run — skipping ArcadeDB connection.")
        return

    import asyncio
    asyncio.run(seed_arcadedb(args.bolt, args.user, args.password, args.database))


if __name__ == "__main__":
    main()
