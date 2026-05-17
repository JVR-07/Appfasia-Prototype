from __future__ import annotations
from datetime import datetime
from uuid import UUID
import asyncpg

async def get_publications_since(conn: asyncpg.Connection, since_dt: datetime) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT id, titulo, resumen, contenido, tags, imagen_url, created_at
        FROM publicaciones
        WHERE created_at > $1
        ORDER BY created_at DESC
        """,
        since_dt
    )
    return [dict(r) for r in rows]

async def get_all_publications(conn: asyncpg.Connection) -> list[dict]:
    rows = await conn.fetch(
        "SELECT id, titulo, resumen, contenido, tags, imagen_url, created_at FROM publicaciones ORDER BY created_at DESC"
    )
    return [dict(r) for r in rows]

async def get_publication_by_id(conn: asyncpg.Connection, pub_id: UUID) -> dict | None:
    row = await conn.fetchrow("SELECT id, titulo, resumen, contenido, tags, imagen_url, created_at FROM publicaciones WHERE id = $1", pub_id)
    return dict(row) if row else None
