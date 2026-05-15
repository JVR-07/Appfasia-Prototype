from typing import Optional, List
from inference_engine.schemas import (
    RawMetrics, BKTState, SessionContext, EngineDecision,
    EngineAction, MinigameType, HardwareMode, AvatarMode
)
from inference_engine.metrics.tra import classify_tra
from inference_engine.rules.dosage_rules import check_session_limit, should_trigger_minigame
from inference_engine.rules.ipf_rules import evaluate_ipf
from inference_engine.rules.tra_rules import evaluate_tra
from inference_engine.rules.lme_rules import evaluate_lme
from inference_engine.memory.ema import should_level_down
from inference_engine.bkt.engine import update as update_bkt
from inference_engine.rules.constants import IPF_MASTERY, P_MASTERY_THRESHOLD


def evaluate(
    metrics: RawMetrics,
    bkt_state: BKTState,
    session_context: SessionContext,
    recent_emas: Optional[List[float]] = None
) -> EngineDecision:
    """
    Main orchestrator. Evaluates a user response through a priority cascade
    and returns a single EngineDecision.

    Evaluation order (highest priority first):
      1. Session limits (dosage)
      2. LOW_CONFIDENCE (STT failed)
      3. TRA classification → VM_BLOCKED or TIMEOUT
      4. Minigame triggers (reward/rescue)
      5. IPF rules → possible HARDWARE_OVERRIDE
      6. LME rules → possible level suggestion
      7. EMA trend → possible LEVEL_DOWN
      8. BKT update → possible ADVANCE (mastery threshold)
      9. Default: REPEAT at current level
    """
    # 1. Dosage limits
    if check_session_limit(
        session_context.level,
        session_context.elapsed_minutes,
        session_context.exercises_done
    ):
        return EngineDecision(action=EngineAction.END_SESSION)

    # 2. LOW_CONFIDENCE
    if metrics.is_low_confidence:
        return EngineDecision(action=EngineAction.REPEAT, avatar_mode=AvatarMode.NEUTRAL)

    # 3. TRA classification
    tra_res = classify_tra(metrics.tra_ms)
    is_correct = metrics.ipf is not None and metrics.ipf >= IPF_MASTERY
    tra_result = evaluate_tra(tra_res, session_context.consecutive_timeouts, is_correct)

    if tra_result.trigger_vm_block:
        return EngineDecision(
            action=EngineAction.HARDWARE_OVERRIDE,
            hardware_override=HardwareMode.T_A,
            avatar_mode=AvatarMode.SUPPORT
        )

    if tra_res.is_timeout:
        return EngineDecision(action=EngineAction.REPEAT, avatar_mode=AvatarMode.SUPPORT)

    # 4. Minigame triggers
    minigame = should_trigger_minigame(
        session_context.consecutive_correct,
        session_context.consecutive_errors
    )
    if minigame is not None:
        avatar = AvatarMode.CHALLENGE if minigame == MinigameType.REWARD else AvatarMode.SUPPORT
        return EngineDecision(action=EngineAction.MINIGAME, minigame_type=minigame, avatar_mode=avatar)

    # 5. IPF rules
    ipf_result = evaluate_ipf(metrics.ipf, metrics.is_low_confidence, session_context.consecutive_errors)
    if ipf_result.trigger_override:
        return EngineDecision(
            action=EngineAction.HARDWARE_OVERRIDE,
            hardware_override=HardwareMode.T_S,
            avatar_mode=AvatarMode.SUPPORT
        )

    # 6. LME rules
    lme_result = evaluate_lme(metrics.lme, session_context.level)
    if lme_result.suggest_level is not None and lme_result.suggest_level > session_context.level:
        return EngineDecision(
            action=EngineAction.ADVANCE,
            requires_graph_query=True,
            target_level=lme_result.suggest_level,
            avatar_mode=AvatarMode.CHALLENGE
        )

    # 7. EMA trend → level down
    if recent_emas and should_level_down(recent_emas):
        return EngineDecision(
            action=EngineAction.LEVEL_DOWN,
            target_level=max(1, session_context.level - 1),
            avatar_mode=AvatarMode.SUPPORT
        )

    # 8. BKT update
    bkt_state.p_mastery = update_bkt(
        p_mastery=bkt_state.p_mastery,
        correct=is_correct,
        p_transit=bkt_state.p_transit,
        p_slip=bkt_state.p_slip,
        p_guess=bkt_state.p_guess
    )

    if bkt_state.p_mastery >= P_MASTERY_THRESHOLD:
        bkt_state.is_mastered = True
        return EngineDecision(
            action=EngineAction.ADVANCE,
            requires_graph_query=True,
            avatar_mode=AvatarMode.CHALLENGE
        )

    # 9. Default: repeat
    return EngineDecision(action=EngineAction.REPEAT, avatar_mode=ipf_result.avatar_mode)


async def evaluate_with_graph(
    metrics: RawMetrics,
    bkt_state: BKTState,
    session_context: SessionContext,
    navigator: 'GraphNavigator',
    mastered_ids: set[str],
    recent_emas: Optional[List[float]] = None,
    lag_tickets: Optional[List['LagTicket']] = None,
    sem_score: Optional['SEMScore'] = None
) -> EngineDecision:
    """
    Extended evaluate() that resolves requires_graph_query.
    
    After the existing cascade:
    - If action == ADVANCE and requires_graph_query:
        → call navigator.get_next_optimal_hito()
        → populate next_hito_id in EngineDecision
    - If lag_tickets exist:
        → inject micro-exercise hitos into decision
    - If sem_score is provided (Narrador/Pensador templates):
        → factor SEM into the correct/incorrect determination
    
    Override logic: If we have SEM, it acts as a gatekeeper for correct/incorrect
    We map SEM to IPF for the basic evaluate() to digest it if sem_score exists
    If SEM < 70, we force a "wrong" evaluation even if other metrics were okay.
    """
    original_ipf = metrics.ipf
    if sem_score and sem_score.is_available:
        if sem_score.score_global >= 70.0:
            # SEM says correct. Ensure IPF reflects this if it was missing/low.
            if metrics.ipf is None or metrics.ipf < IPF_MASTERY:
                metrics.ipf = IPF_MASTERY
        else:
            # SEM says incorrect. Force IPF low so it counts as an error.
            metrics.ipf = 0.0

    decision = evaluate(metrics, bkt_state, session_context, recent_emas)
    
    # Restore original metric for cleanliness
    metrics.ipf = original_ipf

    if lag_tickets and decision.action in (EngineAction.REPEAT, EngineAction.ADVANCE):
        from inference_engine.graph.lag_detector import LagDetector
        detector = LagDetector(navigator)
        micro_hitos = await detector.get_micro_exercise_hitos(lag_tickets, max_count=2)
        if micro_hitos:
            decision.requires_graph_query = False
            decision.target_level = None 
            setattr(decision, "next_hito_id", micro_hitos[0]) 

    if decision.action == EngineAction.ADVANCE and decision.requires_graph_query:
        next_hito = await navigator.get_next_optimal_hito(mastered_ids, session_context.level)
        if next_hito:
            setattr(decision, "next_hito_id", next_hito.id_hito)
            decision.target_level = next_hito.nivel
        else:
            # Reached end of graph for this level
            pass
        decision.requires_graph_query = False

    return decision
