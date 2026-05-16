"""
Tests for GET /progress/{child_id}, GET /sessions, POST /label, POST /external-advance.
Uses child_authed_client + mock_db.
"""
from __future__ import annotations

from uuid import UUID, uuid4
from datetime import datetime, timezone

import pytest

from tests.api.conftest import CHILD_ID, TUTOR_ID


def _session_row(estado="COMPLETADA", ipf=81.2, ejercicios=4):
    return {
        "id_sesion": uuid4(),
        "id_child": CHILD_ID,
        "fecha_inicio": datetime.now(timezone.utc),
        "fecha_fin": datetime.now(timezone.utc),
        "estado": estado,
        "ejercicios_completados": ejercicios,
        "ipf_promedio": ipf,
        "etiqueta_tutor": None,
    }


class TestGetProgress:
    def test_progress_success(self, child_authed_client, mock_db):
        mock_db.fetchrow.side_effect = [
            # get child (already resolved via child dependency, but progress still queries)
            {"id_child": CHILD_ID, "id_tutor": TUTOR_ID, "nombre": "Lucía",
             "nivel_actual": 2, "diagnostico_ok": True, "racha_dias": 5,
             "fecha_nac": "2020-03-15"},
            # week summary
            {"sesiones_completadas": 4, "minutos_totales": 44, "hitos_dominados": 2},
            # ipf avg
            {"ipf_avg": 81.2},
            # mastery count
            {"dominados": 8},
        ]

        r = child_authed_client.get(f"/api/v1/progress/{CHILD_ID}")
        assert r.status_code == 200
        data = r.json()
        assert data["racha_dias"] == 5
        assert "resumen_semana" in data
        assert "nivel_actual" in data

    def test_progress_not_found(self, authed_client, mock_db):
        mock_db.fetchrow.return_value = None
        r = authed_client.get(f"/api/v1/progress/{uuid4()}")
        assert r.status_code == 404


class TestGetSessions:
    def test_sessions_paginated(self, child_authed_client, mock_db):
        # child ownership check
        mock_db.fetchrow.return_value = {"id_child": CHILD_ID}
        mock_db.fetchval.return_value = 3
        mock_db.fetch.return_value = [_session_row(), _session_row(), _session_row()]

        r = child_authed_client.get(f"/api/v1/progress/{CHILD_ID}/sessions?limit=10&offset=0")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 3
        assert len(data["sessions"]) == 3

    def test_sessions_empty(self, child_authed_client, mock_db):
        mock_db.fetchrow.return_value = {"id_child": CHILD_ID}
        mock_db.fetchval.return_value = 0
        mock_db.fetch.return_value = []

        r = child_authed_client.get(f"/api/v1/progress/{CHILD_ID}/sessions")
        assert r.status_code == 200
        assert r.json()["total"] == 0


class TestLabelSession:
    def test_label_valid(self, child_authed_client, mock_db):
        session_id = uuid4()
        mock_db.fetchrow.return_value = {"id_sesion": session_id}
        mock_db.execute.return_value = None

        r = child_authed_client.post(
            f"/api/v1/progress/{CHILD_ID}/sessions/{session_id}/label",
            json={"etiqueta": "Cansancio", "nota": "Durmió mal"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["etiqueta"] == "Cansancio"
        assert data["r0_weight_ajustado"] == 0.2

    def test_label_invalid_value(self, child_authed_client, mock_db):
        r = child_authed_client.post(
            f"/api/v1/progress/{CHILD_ID}/sessions/{uuid4()}/label",
            json={"etiqueta": "No_existe"},
        )
        assert r.status_code == 400

    def test_label_session_not_found(self, child_authed_client, mock_db):
        mock_db.fetchrow.return_value = None
        r = child_authed_client.post(
            f"/api/v1/progress/{CHILD_ID}/sessions/{uuid4()}/label",
            json={"etiqueta": "Distracción"},
        )
        assert r.status_code == 404

    @pytest.mark.parametrize("etiqueta,expected_r0", [
        ("Enfermedad", 0.1),
        ("Cansancio", 0.2),
        ("Distracción", 0.3),
        ("Otro", 0.4),
    ])
    def test_r0_weight_mapping(self, child_authed_client, mock_db, etiqueta, expected_r0):
        session_id = uuid4()
        mock_db.fetchrow.return_value = {"id_sesion": session_id}
        mock_db.execute.return_value = None

        r = child_authed_client.post(
            f"/api/v1/progress/{CHILD_ID}/sessions/{session_id}/label",
            json={"etiqueta": etiqueta},
        )
        assert r.status_code == 200
        assert r.json()["r0_weight_ajustado"] == expected_r0


class TestExternalAdvance:
    def test_external_advance_schedules_verification(self, child_authed_client, mock_db, fake_redis):
        mock_db.fetchrow.return_value = {"id_child": CHILD_ID}

        r = child_authed_client.post(
            f"/api/v1/progress/{CHILD_ID}/external-advance",
            json={
                "descripcion": "Dijo su primera oración completa",
                "id_hito_relacionado": "H_N2_001",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["prueba_verificacion_programada"] is True
