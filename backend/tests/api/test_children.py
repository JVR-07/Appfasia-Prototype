"""
Tests for GET/POST/PUT /children/*.
Uses authed_client (JWT bypassed) + mock_db.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID

import pytest

from tests.api.conftest import TUTOR_ID, CHILD_ID, TUTOR_DICT, CHILD_DICT
from db.rows import ChildRow


def _make_child_record(nombre="Lucía", nivel=2):
    return {
        "id_child": CHILD_ID,
        "id_tutor": TUTOR_ID,
        "nombre": nombre,
        "fecha_nac": date(2020, 3, 15),
        "nivel_actual": nivel,
        "diagnostico_ok": True,
        "racha_dias": 3,
        "created_at": datetime.now(timezone.utc),
    }


class TestCreateChild:
    def test_create_success(self, authed_client, mock_db):
        mock_db.fetchrow.return_value = _make_child_record("Lucía")

        r = authed_client.post("/api/v1/children", json={
            "nombre": "Lucía", "fecha_nac": "2020-03-15",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["nombre"] == "Lucía"
        assert "edad_meses" in data

    def test_create_invalid_date(self, authed_client):
        r = authed_client.post("/api/v1/children", json={
            "nombre": "Test", "fecha_nac": "not-a-date",
        })
        assert r.status_code == 422

    def test_create_missing_nombre(self, authed_client):
        r = authed_client.post("/api/v1/children", json={"fecha_nac": "2020-03-15"})
        assert r.status_code == 422

    def test_unauthenticated(self, client):
        r = client.post("/api/v1/children", json={"nombre": "Test", "fecha_nac": "2020-01-01"})
        assert r.status_code == 401


class TestListChildren:
    def test_list_returns_empty(self, authed_client, mock_db):
        mock_db.fetch.return_value = []
        r = authed_client.get("/api/v1/children")
        assert r.status_code == 200
        assert r.json() == []

    def test_list_returns_children(self, authed_client, mock_db):
        mock_db.fetch.return_value = [_make_child_record("Lucía"), _make_child_record("Tomás")]
        r = authed_client.get("/api/v1/children")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        assert data[0]["nombre"] == "Lucía"

    def test_age_months_calculated(self, authed_client, mock_db):
        mock_db.fetch.return_value = [_make_child_record()]
        r = authed_client.get("/api/v1/children")
        assert "edad_meses" in r.json()[0]
        assert isinstance(r.json()[0]["edad_meses"], int)


class TestGetChild:
    def test_get_child_success(self, child_authed_client, mock_db):
        # get_child_for_tutor is already overridden with CHILD_DICT
        # We need to mock the BKT summary query
        mock_db.fetchrow.return_value = {
            "hitos_dominados": 5,
            "hitos_en_practica": 2,
            "hitos_sin_iniciar": 10,
        }
        r = child_authed_client.get(f"/api/v1/children/{CHILD_ID}")
        assert r.status_code == 200
        data = r.json()
        assert "bkt_summary" in data
        assert data["bkt_summary"]["hitos_dominados"] == 5

    def test_get_child_not_found(self, authed_client, mock_db):
        from core.dependencies import get_child_for_tutor
        from fastapi import HTTPException
        from main import app

        async def _raise():
            raise HTTPException(status_code=404, detail="Perfil de niño no encontrado o no te pertenece")

        app.dependency_overrides[get_child_for_tutor] = _raise
        import uuid
        r = authed_client.get(f"/api/v1/children/{uuid.uuid4()}")
        assert r.status_code == 404


class TestUpdateChild:
    def test_update_nombre(self, child_authed_client, mock_db):
        mock_db.fetchrow.return_value = {
            **_make_child_record("Luci"), "nombre": "Luci"
        }
        r = child_authed_client.put(f"/api/v1/children/{CHILD_ID}", json={"nombre": "Luci"})
        assert r.status_code == 200
        assert r.json()["nombre"] == "Luci"

    def test_update_nothing_returns_400(self, child_authed_client, mock_db):
        r = child_authed_client.put(f"/api/v1/children/{CHILD_ID}", json={})
        assert r.status_code == 400

    def test_ownership_enforced(self, authed_client, mock_db):
        from core.dependencies import get_child_for_tutor
        from fastapi import HTTPException
        from main import app

        async def _raise():
            raise HTTPException(status_code=404, detail="not found")

        app.dependency_overrides[get_child_for_tutor] = _raise
        import uuid
        r = authed_client.put(f"/api/v1/children/{uuid.uuid4()}", json={"nombre": "X"})
        assert r.status_code == 404
