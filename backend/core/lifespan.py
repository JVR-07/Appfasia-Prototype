from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
from fastapi import FastAPI
from redis.asyncio import Redis

from core.config import settings
from inference_engine.graph.navigator import GraphNavigator, ArcadeDBBackend


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ── Startup ──
    app.state.pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=2,
        max_size=10,
    )
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=False)
    app.state.navigator = GraphNavigator(
        ArcadeDBBackend(
            bolt_uri=settings.arcadedb_bolt,
            user=settings.arcadedb_user,
            password=settings.arcadedb_root_password,
            database=settings.arcadedb_database,
        )
    )

    yield

    # ── Shutdown ──
    await app.state.pool.close()
    await app.state.redis.aclose()
    await app.state.navigator.close()
