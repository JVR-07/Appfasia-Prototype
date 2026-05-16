"""
ChildRepository — all SQL for the 'children' and 'hito_mastery' tables lives here.
"""
from __future__ import annotations

from datetime import date
from uuid import UUID

import asyncpg

from db.rows import ChildRow, HitoMasteryRow


async def create(
    conn: asyncpg.Connection,
    id_tutor: UUID,
    nombre: str,
    fecha_nac: date,
) -> ChildRow:
    r = await conn.fetchrow(
        """
        INSERT INTO children (id_tutor, nombre, fecha_nac)
        VALUES ($1, $2, $3)
        RETURNING *
        """,
        id_tutor, nombre, fecha_nac,
    )
    return ChildRow.from_record(r)


async def find_by_id(conn: asyncpg.Connection, child_id: UUID) -> ChildRow | None:
    r = await conn.fetchrow(
        "SELECT * FROM children WHERE id_child = $1", child_id
    )
    return ChildRow.from_record(r) if r else None


async def find_by_id_and_tutor(
    conn: asyncpg.Connection, child_id: UUID, tutor_id: UUID
) -> ChildRow | None:
    r = await conn.fetchrow(
        "SELECT * FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id, tutor_id,
    )
    return ChildRow.from_record(r) if r else None


async def list_by_tutor(
    conn: asyncpg.Connection, tutor_id: UUID
) -> list[ChildRow]:
    rows = await conn.fetch(
        """
        SELECT * FROM children WHERE id_tutor = $1 ORDER BY created_at
        """,
        tutor_id,
    )
    return [ChildRow.from_record(r) for r in rows]


async def update_nombre(
    conn: asyncpg.Connection, child_id: UUID, nombre: str
) -> ChildRow:
    r = await conn.fetchrow(
        "UPDATE children SET nombre = $1 WHERE id_child = $2 RETURNING *",
        nombre, child_id,
    )
    return ChildRow.from_record(r)


async def update_fecha_nac(
    conn: asyncpg.Connection, child_id: UUID, fecha_nac: date
) -> ChildRow:
    r = await conn.fetchrow(
        "UPDATE children SET fecha_nac = $1 WHERE id_child = $2 RETURNING *",
        fecha_nac, child_id,
    )
    return ChildRow.from_record(r)


async def set_nivel_and_diagnostico(
    conn: asyncpg.Connection, child_id: UUID, nivel: int
) -> None:
    await conn.execute(
        "UPDATE children SET nivel_actual = $1, diagnostico_ok = TRUE WHERE id_child = $2",
        nivel, child_id,
    )


# ── Hito Mastery ──

async def get_mastered_ids(conn: asyncpg.Connection, child_id: UUID) -> set[str]:
    rows = await conn.fetch(
        "SELECT id_hito FROM hito_mastery WHERE id_child = $1 AND is_mastered = TRUE",
        child_id,
    )
    return {r["id_hito"] for r in rows}


async def get_bkt_summary(conn: asyncpg.Connection, child_id: UUID) -> dict:
    r = await conn.fetchrow(
        """
        SELECT
            COUNT(*) FILTER (WHERE is_mastered)                         AS hitos_dominados,
            COUNT(*) FILTER (WHERE NOT is_mastered AND p_mastery > 0)  AS hitos_en_practica,
            COUNT(*) FILTER (WHERE NOT is_mastered AND p_mastery = 0)  AS hitos_sin_iniciar
        FROM hito_mastery WHERE id_child = $1
        """,
        child_id,
    )
    return dict(r)


async def upsert_mastery(
    conn: asyncpg.Connection,
    child_id: UUID,
    id_hito: str,
    p_mastery: float,
    is_mastered: bool,
) -> None:
    await conn.execute(
        """
        INSERT INTO hito_mastery (id_child, id_hito, p_mastery, is_mastered, updated_at)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT (id_child, id_hito) DO UPDATE
        SET p_mastery = EXCLUDED.p_mastery,
            is_mastered = EXCLUDED.is_mastered,
            updated_at = NOW()
        """,
        child_id, id_hito, p_mastery, is_mastered,
    )
