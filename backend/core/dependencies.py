from typing import Annotated
from uuid import UUID

import asyncpg
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from core.security import decode_access_token
from inference_engine.graph.navigator import GraphNavigator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Connection dependencies ──

async def get_db(request: Request) -> asyncpg.Connection:
    async with request.app.state.pool.acquire() as conn:
        yield conn


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


async def get_navigator(request: Request) -> GraphNavigator:
    return request.app.state.navigator


# ── Auth dependencies ──

async def get_current_tutor(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[asyncpg.Connection, Depends(get_db)],
) -> dict:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        tutor_id = decode_access_token(token)
    except ValueError:
        raise credentials_exc

    row = await db.fetchrow(
        "SELECT id, nombre, email FROM tutores WHERE id = $1",
        UUID(tutor_id),
    )
    if row is None:
        raise credentials_exc
    return dict(row)


async def get_child_for_tutor(
    child_id: UUID,
    tutor: Annotated[dict, Depends(get_current_tutor)],
    db: Annotated[asyncpg.Connection, Depends(get_db)],
) -> dict:
    row = await db.fetchrow(
        "SELECT * FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id,
        tutor["id"],
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de niño no encontrado o no te pertenece",
        )
    return dict(row)


# ── Typed aliases for cleaner route signatures ──

DBConn = Annotated[asyncpg.Connection, Depends(get_db)]
RedisConn = Annotated[Redis, Depends(get_redis)]
Navigator = Annotated[GraphNavigator, Depends(get_navigator)]
CurrentTutor = Annotated[dict, Depends(get_current_tutor)]
ChildRow = Annotated[dict, Depends(get_child_for_tutor)]
