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
