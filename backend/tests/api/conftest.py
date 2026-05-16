"""
Shared fixtures for API integration tests.

Strategy: we override FastAPI dependencies so tests never need a real
PostgreSQL, Redis, or ArcadeDB instance.

  get_db       → AsyncMock (asyncpg.Connection)
  get_redis    → FakeRedis
  get_navigator → GraphNavigator(NetworkXBackend)
  get_current_tutor → returns a fixed tutor dict (no JWT validation)
"""
from __future__ import annotations

import os
import uuid
from unittest.mock import AsyncMock, MagicMock

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

# Set a dummy .env before importing settings-dependent modules
os.environ.setdefault("DATABASE_URL", "postgresql://x:x@localhost/x")
os.environ.setdefault("ARCADEDB_BOLT", "bolt://localhost:7687")
os.environ.setdefault("ARCADEDB_USER", "root")
os.environ.setdefault("ARCADEDB_DATABASE", "test")
os.environ.setdefault("ARCADEDB_ROOT_PASSWORD", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests-only")
os.environ.setdefault("AZURE_SPEECH_KEY", "mock")
os.environ.setdefault("AZURE_SPEECH_REGION", "eastus")
os.environ.setdefault("GEMINI_API_KEY", "fake")

from main import app
from core.dependencies import (
    get_db, get_redis, get_navigator, get_current_tutor, get_child_for_tutor
)
from inference_engine.graph.navigator import GraphNavigator, NetworkXBackend


# ── Fixed test IDs ──
TUTOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
CHILD_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
SESSION_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")

TUTOR_DICT = {
    "id": TUTOR_ID,
    "nombre": "Tutor Test",
    "email": "test@appfasia.com",
}

CHILD_DICT = {
    "id_child": CHILD_ID,
    "id_tutor": TUTOR_ID,
    "nombre": "Lucía",
    "fecha_nac": "2020-03-15",
    "nivel_actual": 2,
    "diagnostico_ok": True,
    "racha_dias": 3,
    "created_at": "2026-01-01T00:00:00",
}


@pytest.fixture
def mock_db():
    """Returns an AsyncMock that behaves like an asyncpg.Connection."""
    conn = AsyncMock()
    # Sensible defaults — override per test as needed
    conn.fetchrow.return_value = None
    conn.fetch.return_value = []
    conn.fetchval.return_value = None
    conn.execute.return_value = None
    return conn


@pytest.fixture
def fake_redis():
    return fakeredis.aioredis.FakeRedis()


@pytest.fixture
def mock_navigator():
    nav = AsyncMock()
    nav.get_next_optimal_hito.return_value = None
    return nav


@pytest.fixture
def client(mock_db, fake_redis, mock_navigator):
    """TestClient with all infrastructure dependencies mocked.
    The lifespan is bypassed — no real DB connections are created.
    """
    from contextlib import asynccontextmanager
    from unittest.mock import MagicMock, patch

    async def _override_db():
        yield mock_db

    async def _override_redis():
        return fake_redis

    async def _override_navigator():
        return mock_navigator

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_redis] = _override_redis
    app.dependency_overrides[get_navigator] = _override_navigator

    # Bypass the real lifespan (no asyncpg.create_pool, no Redis.from_url, etc.)
    @asynccontextmanager
    async def _noop_lifespan(app):
        app.state.pool = MagicMock()
        app.state.redis = fake_redis
        app.state.navigator = mock_navigator
        yield

    app.router.lifespan_context = _noop_lifespan

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def authed_client(client, mock_db):
    """TestClient pre-authenticated as TUTOR_DICT (skips JWT validation)."""
    app.dependency_overrides[get_current_tutor] = lambda: TUTOR_DICT
    yield client
    # get_current_tutor override cleared by parent client fixture teardown


@pytest.fixture
def child_authed_client(authed_client):
    """TestClient pre-authenticated + child ownership already resolved."""
    app.dependency_overrides[get_child_for_tutor] = lambda: CHILD_DICT
    yield authed_client
