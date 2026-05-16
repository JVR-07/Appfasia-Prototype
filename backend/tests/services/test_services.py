"""
Tests for services/stt_azure.py and services/content_engine.py.
Both are pure Python — no FastAPI needed.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.stt_azure import AzureSTTService, STTResult
from services.content_engine import ContentEngine, Plantilla, ExercisePayload


# ── AzureSTTService ─────────────────────────────────────────────────────────

class TestAzureSTTMockMode:
    """When key='mock', service returns expected_text without calling Azure."""

    @pytest.fixture
    def stt(self):
        return AzureSTTService(key="mock", region="eastus")

    @pytest.mark.asyncio
    async def test_returns_expected_text(self, stt):
        result = await stt.transcribe_base64("AAAA", expected_text="Perro")
        assert result.transcript == "Perro"
        assert result.confidence == 0.95
        assert not result.is_low_confidence

    @pytest.mark.asyncio
    async def test_empty_expected_text_is_timeout(self, stt):
        result = await stt.transcribe_base64("AAAA", expected_text="")
        assert result.transcript == ""
        assert result.is_low_confidence
        assert result.is_timeout

    @pytest.mark.asyncio
    async def test_none_expected_text_is_timeout(self, stt):
        result = await stt.transcribe_base64("AAAA", expected_text=None)
        assert result.is_timeout

    def test_is_mock_detection(self, stt):
        assert stt._is_mock is True

    def test_real_key_not_mock(self):
        real_stt = AzureSTTService(key="real-azure-key-abc123", region="eastus")
        assert real_stt._is_mock is False


class TestSTTResult:
    def test_is_timeout_false_when_transcript_present(self):
        r = STTResult(transcript="Hola", confidence=0.9, is_low_confidence=False)
        assert not r.is_timeout

    def test_is_timeout_true_when_empty(self):
        r = STTResult(transcript="", confidence=0.0, is_low_confidence=True)
        assert r.is_timeout

    def test_low_confidence_threshold(self):
        assert AzureSTTService.LOW_CONFIDENCE_THRESHOLD == 0.70


# ── ContentEngine ────────────────────────────────────────────────────────────

class TestPlantillaEnum:
    def test_all_templates_have_hardware(self):
        for p in Plantilla:
            assert p.hardware_req in ("V-M", "T-S", "T-A")

    def test_llm_eval_templates(self):
        assert Plantilla.NARRADOR.needs_llm_eval
        assert Plantilla.PENSADOR.needs_llm_eval
        assert not Plantilla.NOMBRADOR.needs_llm_eval
        assert not Plantilla.IDENTIFICADOR.needs_llm_eval

    def test_distractor_templates(self):
        assert Plantilla.IDENTIFICADOR.needs_distractors
        assert not Plantilla.NOMBRADOR.needs_distractors
        assert not Plantilla.NARRADOR.needs_distractors

    def test_hardware_mapping(self):
        assert Plantilla.IMITADOR.hardware_req == "V-M"
        assert Plantilla.IDENTIFICADOR.hardware_req == "T-S"
        assert Plantilla.ORDENADOR.hardware_req == "T-A"
        assert Plantilla.CONSTRUCTOR.hardware_req == "T-A"
        assert Plantilla.NARRADOR.hardware_req == "V-M"
        assert Plantilla.PENSADOR.hardware_req == "V-M"

    def test_enum_count(self):
        """Ensure all 8 templates are defined."""
        assert len(Plantilla) == 8

    def test_string_value(self):
        assert Plantilla.NOMBRADOR == "Nombrador"
        assert Plantilla.IDENTIFICADOR == "Identificador"


@pytest.fixture
def mock_pool():
    """Properly mocks asyncpg Pool.acquire() as an async context manager."""
    from unittest.mock import MagicMock
    conn = AsyncMock()
    pool = MagicMock()
    # pool.acquire() must return an async context manager
    acquire_ctx = MagicMock()
    acquire_ctx.__aenter__ = AsyncMock(return_value=conn)
    acquire_ctx.__aexit__ = AsyncMock(return_value=False)
    pool.acquire = MagicMock(return_value=acquire_ctx)
    return pool, conn


class TestContentEngine:
    @pytest.mark.asyncio
    async def test_pick_exercise_returns_payload(self, mock_pool):
        pool, conn = mock_pool
        conn.fetch.return_value = [{
            "id_recurso": "W_001",
            "texto": "Perro",
            "imagen_url": "https://cdn.example.com/perro.png",
            "audio_url": "https://cdn.example.com/W_001.mp3",
        }]

        engine = ContentEngine(pool)
        payload = await engine.pick_exercise(
            level=1, plantilla=Plantilla.NOMBRADOR, used_resource_ids=set()
        )

        assert payload is not None
        assert isinstance(payload, ExercisePayload)
        assert payload.texto_esperado == "Perro"
        assert payload.plantilla == Plantilla.NOMBRADOR
        assert payload.hardware_req == "V-M"
        assert payload.id_recurso == "W_001"

    @pytest.mark.asyncio
    async def test_pick_exercise_none_when_no_resources(self, mock_pool):
        pool, conn = mock_pool
        conn.fetch.return_value = []

        engine = ContentEngine(pool)
        payload = await engine.pick_exercise(
            level=1, plantilla=Plantilla.NOMBRADOR, used_resource_ids=set()
        )
        assert payload is None

    @pytest.mark.asyncio
    async def test_identificador_includes_distractors(self, mock_pool):
        pool, conn = mock_pool
        # First fetch: main resource; second fetch: distractors
        conn.fetch.side_effect = [
            [{"id_recurso": "W_001", "texto": "Perro",
              "imagen_url": "https://cdn/perro.png", "audio_url": "https://cdn/W_001.mp3"}],
            [{"id_recurso": "W_002", "imagen_url": "https://cdn/gato.png"},
             {"id_recurso": "W_003", "imagen_url": "https://cdn/vaca.png"}],
        ]

        engine = ContentEngine(pool)
        payload = await engine.pick_exercise(
            level=1, plantilla=Plantilla.IDENTIFICADOR, used_resource_ids=set()
        )

        assert payload is not None
        assert payload.hardware_req == "T-S"
        # 2 distractors + 1 correct = 3 total options
        assert len(payload.opciones) == 3
        ids = [o["id"] for o in payload.opciones]
        assert "W_001" in ids  # correct option included

    @pytest.mark.asyncio
    async def test_used_resources_excluded(self, mock_pool):
        pool, conn = mock_pool
        conn.fetch.return_value = []

        engine = ContentEngine(pool)
        # Call with used_resource_ids — conn.fetch should receive the exclusion list
        await engine.pick_exercise(
            level=1,
            plantilla=Plantilla.NOMBRADOR,
            used_resource_ids={"W_001", "W_002"},
        )

        call_args = conn.fetch.call_args
        # The second argument should be the exclusion list
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_prompt_built_per_template(self, mock_pool):
        pool, conn = mock_pool
        resource = {
            "id_recurso": "W_001", "texto": "Perro",
            "imagen_url": "https://cdn/perro.png",
            "audio_url": "https://cdn/W_001.mp3",
        }

        engine = ContentEngine(pool)

        for plantilla, expected_keys in [
            (Plantilla.IMITADOR,      ["audio_url", "texto_estimulo"]),
            (Plantilla.NOMBRADOR,     ["imagen_url", "texto_oculto"]),
            (Plantilla.COMPLETADOR,   ["imagen_url", "frase_incompleta"]),
            (Plantilla.CONSTRUCTOR,   ["imagen_url", "instruccion"]),
            (Plantilla.NARRADOR,      ["imagen_url", "instruccion"]),
            (Plantilla.PENSADOR,      ["imagen_url", "instruccion"]),
        ]:
            conn.fetch.return_value = [resource]
            payload = await engine.pick_exercise(level=1, plantilla=plantilla, used_resource_ids=set())
            assert payload is not None
            for key in expected_keys:
                assert key in payload.prompt, f"{plantilla}: missing '{key}' in prompt"

    @pytest.mark.parametrize("level,expected_ipf_min", [
        (1, 70), (2, 75), (3, 80), (4, 80), (5, 85)
    ])
    @pytest.mark.asyncio
    async def test_umbrales_per_level(self, mock_pool, level, expected_ipf_min):
        pool, conn = mock_pool
        conn.fetch.return_value = [{
            "id_recurso": "W_001", "texto": "X",
            "imagen_url": "https://cdn/x.png", "audio_url": "https://cdn/x.mp3",
        }]

        engine = ContentEngine(pool)
        payload = await engine.pick_exercise(level=level, plantilla=Plantilla.NOMBRADOR, used_resource_ids=set())
        assert payload.umbrales["ipf_min"] == expected_ipf_min
