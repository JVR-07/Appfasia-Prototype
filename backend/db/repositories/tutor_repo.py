"""
TutorRepository — all SQL for the 'tutores' table lives here.
Routes never write raw SQL for tutores; they call these functions.
"""
from __future__ import annotations

from uuid import UUID

import asyncpg

from db.rows import TutorRow


async def find_by_email(conn: asyncpg.Connection, email: str) -> TutorRow | None:
    r = await conn.fetchrow(
        "SELECT id, nombre, email, created_at FROM tutores WHERE email = $1",
        email,
    )
    return TutorRow.from_record(r) if r else None


async def find_by_id(conn: asyncpg.Connection, tutor_id: UUID) -> TutorRow | None:
    r = await conn.fetchrow(
        "SELECT id, nombre, email, created_at FROM tutores WHERE id = $1",
        tutor_id,
    )
    return TutorRow.from_record(r) if r else None


async def create(
    conn: asyncpg.Connection, nombre: str, email: str, password_hash: str
) -> TutorRow:
    r = await conn.fetchrow(
        """
        INSERT INTO tutores (nombre, email, password_hash)
        VALUES ($1, $2, $3)
        RETURNING id, nombre, email, created_at
        """,
        nombre, email, password_hash,
    )
    return TutorRow.from_record(r)


async def get_password_hash(conn: asyncpg.Connection, email: str) -> str | None:
    """Returns hashed password for login verification, or None if not found."""
    return await conn.fetchval(
        "SELECT password_hash FROM tutores WHERE email = $1", email
    )


async def store_refresh_token(
    conn: asyncpg.Connection,
    tutor_id: UUID,
    token_hash: str,
    expires_at,
) -> None:
    await conn.execute(
        """
        INSERT INTO refresh_tokens (id_tutor, token_hash, expires_at)
        VALUES ($1, $2, $3)
        """,
        tutor_id, token_hash, expires_at,
    )


async def find_valid_refresh_token(
    conn: asyncpg.Connection, tutor_id: UUID, token_hash: str
) -> bool:
    """Returns True if the token exists, is not revoked, and hasn't expired."""
    row = await conn.fetchrow(
        """
        SELECT id FROM refresh_tokens
        WHERE id_tutor = $1 AND token_hash = $2
          AND revoked = FALSE AND expires_at > NOW()
        """,
        tutor_id, token_hash,
    )
    return row is not None
