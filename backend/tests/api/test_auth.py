"""
Tests for POST /auth/register, /auth/login, /auth/refresh, GET /auth/me.
All DB calls go through mock_db (AsyncMock asyncpg.Connection).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from hashlib import sha256
from unittest.mock import AsyncMock, patch

import pytest

from core.security import hash_password, create_access_token, create_refresh_token
from tests.api.conftest import TUTOR_ID, TUTOR_DICT


# ── /auth/register ──────────────────────────────────────────────────────────

class TestRegister:
    def test_register_success(self, client, mock_db):
        # No existing tutor found
        mock_db.fetchrow.side_effect = [
            None,  # find_by_email → not found
            {      # create → new tutor
                "id": TUTOR_ID, "nombre": "María",
                "email": "maria@test.com", "created_at": datetime.now(timezone.utc),
            },
        ]

        r = client.post("/api/v1/auth/register", json={
            "nombre": "María", "email": "maria@test.com", "password": "Secret123",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "maria@test.com"
        assert "id_tutor" in data

    def test_register_duplicate_email(self, client, mock_db):
        mock_db.fetchrow.return_value = {
            "id": TUTOR_ID, "nombre": "Existing",
            "email": "dup@test.com", "created_at": datetime.now(timezone.utc),
        }
        r = client.post("/api/v1/auth/register", json={
            "nombre": "New", "email": "dup@test.com", "password": "Secret123",
        })
        assert r.status_code == 409

    def test_register_invalid_email(self, client, mock_db):
        r = client.post("/api/v1/auth/register", json={
            "nombre": "Test", "email": "not-an-email", "password": "Secret123",
        })
        assert r.status_code == 422

    def test_register_missing_fields(self, client):
        r = client.post("/api/v1/auth/register", json={"nombre": "Test"})
        assert r.status_code == 422


# ── /auth/login ─────────────────────────────────────────────────────────────

class TestLogin:
    def test_login_success(self, client, mock_db):
        pw_hash = hash_password("CorrectPass")
        mock_db.fetchval.return_value = pw_hash  # get_password_hash
        mock_db.fetchrow.return_value = {
            "id": TUTOR_ID, "nombre": "Test",
            "email": "t@t.com", "created_at": datetime.now(timezone.utc),
        }
        mock_db.execute.return_value = None  # store_refresh_token

        r = client.post("/api/v1/auth/login", json={
            "email": "t@t.com", "password": "CorrectPass",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, mock_db):
        mock_db.fetchval.return_value = hash_password("CorrectPass")
        mock_db.fetchrow.return_value = {
            "id": TUTOR_ID, "nombre": "Test",
            "email": "t@t.com", "created_at": datetime.now(timezone.utc),
        }

        r = client.post("/api/v1/auth/login", json={
            "email": "t@t.com", "password": "WrongPass",
        })
        assert r.status_code == 401

    def test_login_nonexistent_user(self, client, mock_db):
        mock_db.fetchval.return_value = None
        mock_db.fetchrow.return_value = None

        r = client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com", "password": "Pass",
        })
        assert r.status_code == 401


# ── /auth/refresh ────────────────────────────────────────────────────────────

class TestRefresh:
    def test_refresh_success(self, client, mock_db):
        refresh_token = create_refresh_token(str(TUTOR_ID))
        token_hash = sha256(refresh_token.encode()).hexdigest()

        # find_valid_refresh_token returns a row (truthy)
        mock_db.fetchrow.return_value = {"id": uuid.uuid4()}

        r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_refresh_invalid_token(self, client, mock_db):
        r = client.post("/api/v1/auth/refresh", json={"refresh_token": "not.a.jwt.token"})
        assert r.status_code == 401

    def test_refresh_revoked_token(self, client, mock_db):
        refresh_token = create_refresh_token(str(TUTOR_ID))
        mock_db.fetchrow.return_value = None  # revoked / not found

        r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert r.status_code == 401


# ── GET /auth/me ─────────────────────────────────────────────────────────────

class TestMe:
    def test_me_authenticated(self, authed_client):
        r = authed_client.get("/api/v1/auth/me")
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == TUTOR_DICT["email"]

    def test_me_no_token(self, client):
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 401

    def test_me_bad_token(self, client, mock_db):
        mock_db.fetchrow.return_value = None
        r = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert r.status_code == 401
