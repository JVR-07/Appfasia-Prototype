import pytest
from unittest.mock import AsyncMock, patch

from inference_engine.schemas import (
    RawMetrics, BKTState, SessionContext, EngineAction, SEMScore
)
from inference_engine.decision.engine import evaluate_with_graph
from inference_engine.graph.schemas import HitoNode, HitoDimension, LagTicket


@pytest.fixture
def mock_navigator():
    nav = AsyncMock()
    # By default, don't return a next_hito
    nav.get_next_optimal_hito.return_value = None
    return nav


@pytest.fixture
def base_metrics():
    return RawMetrics(tra_ms=2000, ipf=85.0, lme=None, is_low_confidence=False, is_timeout=False)


@pytest.fixture
def base_bkt():
    return BKTState(hito_id="H1", p_mastery=0.4, p_transit=0.2, p_slip=0.1, p_guess=0.2)


@pytest.fixture
def base_context():
    return SessionContext(level=2, consecutive_correct=0, consecutive_errors=0, consecutive_timeouts=0, exercises_done=0, elapsed_minutes=0.0)


@pytest.mark.asyncio
async def test_sem_score_overrides_ipf_when_high(mock_navigator, base_metrics, base_bkt, base_context):
    # Set low IPF, would normally be a slip/error
    base_metrics.ipf = 50.0
    sem = SEMScore(score_global=80.0, dimensions={}, rubric_type="narration", is_available=True)
    
    # Evaluate with graph
    decision = await evaluate_with_graph(
        base_metrics, base_bkt, base_context, mock_navigator, set(), sem_score=sem
    )
    
    # Because SEM was >= 70, BKT should update as correct.
    # So p_mastery should increase from 0.4.
    assert base_bkt.p_mastery > 0.4
    # The original metric should be restored
    assert base_metrics.ipf == 50.0


@pytest.mark.asyncio
async def test_sem_score_overrides_ipf_when_low(mock_navigator, base_metrics, base_bkt, base_context):
    # Set high IPF, would normally be correct
    base_metrics.ipf = 90.0
    sem = SEMScore(score_global=60.0, dimensions={}, rubric_type="narration", is_available=True)
    
    # Evaluate with graph
    decision = await evaluate_with_graph(
        base_metrics, base_bkt, base_context, mock_navigator, set(), sem_score=sem
    )
    
    # Because SEM was < 70, BKT should update as incorrect.
    # So p_mastery should decrease from 0.4.
    assert base_bkt.p_mastery < 0.4
    # The original metric should be restored
    assert base_metrics.ipf == 90.0


@pytest.mark.asyncio
async def test_lag_tickets_inject_micro_exercise(mock_navigator, base_metrics, base_bkt, base_context):
    # Simulate a REPEAT decision (normal flow)
    lag = LagTicket(child_level=4, lag_hito_id="H1", lag_level=1, recovery_hitos=["H_RECOVERY"])
    
    with patch("inference_engine.graph.lag_detector.LagDetector") as mock_detector_class:
        mock_detector = AsyncMock()
        mock_detector.get_micro_exercise_hitos.return_value = ["H_RECOVERY"]
        mock_detector_class.return_value = mock_detector
        
        decision = await evaluate_with_graph(
            base_metrics, base_bkt, base_context, mock_navigator, set(), lag_tickets=[lag]
        )
        
        assert getattr(decision, "next_hito_id", None) == "H_RECOVERY"
        assert decision.requires_graph_query is False
        assert decision.target_level is None


@pytest.mark.asyncio
async def test_advance_triggers_graph_query(mock_navigator, base_metrics, base_bkt, base_context):
    # Force mastery to trigger ADVANCE
    base_bkt.p_mastery = 0.99
    
    mock_hito = HitoNode(
        id_hito="H2", nombre="Hito 2", nivel=2, rango_edad_min=0, rango_edad_max=12,
        dimension=HitoDimension.EXPRESIVO, es_bloqueante=False, orden_interno=2
    )
    mock_navigator.get_next_optimal_hito.return_value = mock_hito
    
    decision = await evaluate_with_graph(
        base_metrics, base_bkt, base_context, mock_navigator, set()
    )
    
    assert decision.action == EngineAction.ADVANCE
    # Graph query should have been processed and cleared
    assert decision.requires_graph_query is False
    assert getattr(decision, "next_hito_id", None) == "H2"
    assert decision.target_level == 2
    mock_navigator.get_next_optimal_hito.assert_called_once()
