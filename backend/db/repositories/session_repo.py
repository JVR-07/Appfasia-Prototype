"""
SessionRepository — all SQL for 'sesiones' and 'resultados_ejercicio' tables.
"""
from __future__ import annotations

from uuid import UUID

import asyncpg

from db.rows import SessionRow


async def create_session(
    conn: asyncpg.Connection,
    session_id: UUID,
    child_id: UUID,
    nivel: int,
) -> None:
    await conn.execute(
        """
        INSERT INTO sesiones (id_sesion, id_child, nivel_sesion, estado)
        VALUES ($1, $2, $3, 'EN_CURSO')
        """,
        session_id, child_id, nivel,
    )


async def find_active(
    conn: asyncpg.Connection, session_id: UUID
) -> SessionRow | None:
    r = await conn.fetchrow(
        "SELECT * FROM sesiones WHERE id_sesion = $1 AND estado = 'EN_CURSO'",
        session_id,
    )
    return SessionRow.from_record(r) if r else None


async def count_today(conn: asyncpg.Connection, child_id: UUID) -> int:
    return await conn.fetchval(
        """
        SELECT COUNT(*) FROM sesiones
        WHERE id_child = $1 AND DATE(fecha_inicio) = CURRENT_DATE
        """,
        child_id,
    )


async def complete_session(
    conn: asyncpg.Connection,
    session_id: UUID,
    ejercicios_completados: int,
    ipf_promedio: float,
    hitos_dominados_hoy: int,
) -> None:
    await conn.execute(
        """
        UPDATE sesiones
        SET estado = 'COMPLETADA', fecha_fin = NOW(),
            ejercicios_completados = $1, ipf_promedio = $2,
            hitos_dominados_hoy = $3
        WHERE id_sesion = $4
        """,
        ejercicios_completados, ipf_promedio, hitos_dominados_hoy, session_id,
    )


async def interrupt_session(
    conn: asyncpg.Connection, session_id: UUID, ejercicios_completados: int
) -> None:
    await conn.execute(
        """
        UPDATE sesiones
        SET estado = 'INTERRUMPIDA', fecha_fin = NOW(),
            ejercicios_completados = $1
        WHERE id_sesion = $2
        """,
        ejercicios_completados, session_id,
    )


async def log_result(
    conn: asyncpg.Connection,
    session_id: UUID,
    id_recurso: str | None,
    id_hito: str | None,
    plantilla: str,
    hardware_req: str,
    lme: float | None,
    ipf: float | None,
    tra_ms: int,
    es_correcto: bool,
    es_timeout: bool,
) -> None:
    await conn.execute(
        """
        INSERT INTO resultados_ejercicio
            (id_sesion, id_recurso, id_hito, plantilla, hardware_req,
             lme, ipf, tra_ms, es_correcto, es_timeout)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
        session_id, id_recurso, id_hito, plantilla, hardware_req,
        lme, ipf, tra_ms, es_correcto, es_timeout,
    )


async def get_ipf_average(conn: asyncpg.Connection, session_id: UUID) -> float:
    val = await conn.fetchval(
        "SELECT AVG(ipf) FROM resultados_ejercicio WHERE id_sesion = $1 AND ipf IS NOT NULL",
        session_id,
    )
    return round(float(val or 0), 1)


async def count_results(conn: asyncpg.Connection, session_id: UUID) -> int:
    return await conn.fetchval(
        "SELECT COUNT(*) FROM resultados_ejercicio WHERE id_sesion = $1",
        session_id,
    )
