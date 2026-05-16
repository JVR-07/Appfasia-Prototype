from uuid import UUID, uuid4

import asyncpg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.config import settings
from core.dependencies import DBConn, CurrentTutor, Navigator, RedisConn
from inference_engine.decision.engine import evaluate_with_graph
from inference_engine.metrics.ipf import compute_ipf
from inference_engine.metrics.lme import compute_lme
from inference_engine.metrics.tra import classify_tra
from inference_engine.persistence.redis_state import RedisStateManager
from inference_engine.persistence.redis_spaced_rep import RedisSpacedRepManager
from inference_engine.memory.spaced_repetition import should_enqueue
from inference_engine.schemas import (
    RawMetrics, BKTState, SessionContext, EngineAction,
)
from services.stt_azure import AzureSTTService
from services.content_engine import ContentEngine

router = APIRouter()

_stt = AzureSTTService(
    key=settings.azure_speech_key,
    region=settings.azure_speech_region,
)

_SESION_TTL = 86400  # 24h
_SESSION_KEY = "session:active:{child_id}"


def _sess_key(child_id: str) -> str:
    return f"session:active:{child_id}"


def _meta_key(session_id: str) -> str:
    return f"session:meta:{session_id}"


class StartRequest(BaseModel):
    child_id: str


class ResponseRequest(BaseModel):
    session_id: str
    id_actividad: str
    tipo_respuesta: str
    audio_base64: str | None = None
    id_seleccionado: str | None = None
    texto_esperado: str | None = None
    id_recurso: str | None = None
    id_hito: str | None = None
    plantilla: str = "Nombrador"
    tra_ms: int = 0
    es_timeout: bool = False


# ── Helpers ──

async def _get_mastered_ids(child_id: UUID, db: asyncpg.Connection) -> set[str]:
    rows = await db.fetch(
        "SELECT id_hito FROM hito_mastery WHERE id_child = $1 AND is_mastered = TRUE",
        child_id,
    )
    return {r["id_hito"] for r in rows}


async def _check_daily_limit(child_id: UUID, db: asyncpg.Connection, level: int) -> bool:
    """True if limit is reached."""
    from inference_engine.rules.dosage_rules import check_session_limit
    count = await db.fetchval(
        "SELECT COUNT(*) FROM sesiones WHERE id_child = $1 AND DATE(fecha_inicio) = CURRENT_DATE",
        child_id,
    )
    return count > 0  # One session per day for prototype


# ── POST /session/start ──

@router.post("/start")
async def start_session(body: StartRequest, tutor: CurrentTutor, db: DBConn, redis: RedisConn, navigator: Navigator):
    child_id = UUID(body.child_id)
    child = await db.fetchrow(
        "SELECT * FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id, tutor["id"],
    )
    if not child:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    if not child["diagnostico_ok"]:
        raise HTTPException(status_code=403, detail="DIAGNOSTIC_REQUIRED")

    level = child["nivel_actual"]

    if await _check_daily_limit(child_id, db, level):
        from datetime import timedelta
        raise HTTPException(
            status_code=403,
            detail={
                "error": "SESSION_LIMIT_REACHED",
                "message": f"{child['nombre']} ya completó su sesión de hoy. ¡Vuelve mañana!",
            },
        )

    session_id = str(uuid4())
    mastered = await _get_mastered_ids(child_id, db)
    next_hito = await navigator.get_next_optimal_hito(mastered, level)

    content = ContentEngine(db._con._protocol._transport._extra.get("pool", None))  # injected below
    # Use a global pool reference instead
    exercise = None

    # Store session state in Redis
    state_mgr = RedisStateManager(redis)
    ctx = SessionContext(
        level=level,
        consecutive_correct=0,
        consecutive_errors=0,
        consecutive_timeouts=0,
        exercises_done=0,
        elapsed_minutes=0.0,
    )
    bkt = BKTState(
        hito_id=next_hito.id_hito if next_hito else "UNKNOWN",
        p_mastery=0.3,
        p_transit=0.09,
        p_slip=0.1,
        p_guess=0.2,
    )
    await state_mgr.save_bkt_state(str(child_id), bkt)
    await state_mgr.save_session_context(str(child_id), ctx)

    # Create session in PostgreSQL
    await db.execute(
        """
        INSERT INTO sesiones (id_sesion, id_child, nivel_sesion, estado)
        VALUES ($1, $2, $3, 'EN_CURSO')
        """,
        UUID(session_id), child_id, level,
    )

    # Store active session pointer in Redis
    await redis.setex(_sess_key(str(child_id)), _SESION_TTL, session_id)

    return {
        "session_id": session_id,
        "child_id": str(child_id),
        "nivel_sesion": level,
        "hito_actual": next_hito.id_hito if next_hito else None,
        "avatar_mensaje": f"¡Hola, {child['nombre']}! ¿Lista para jugar?",
    }


# ── POST /session/response ──

@router.post("/response")
async def session_response(body: ResponseRequest, tutor: CurrentTutor, db: DBConn, redis: RedisConn, navigator: Navigator):
    session_id = UUID(body.session_id)
    session_row = await db.fetchrow(
        """
        SELECT s.*, c.id_tutor FROM sesiones s
        JOIN children c ON c.id_child = s.id_child
        WHERE s.id_sesion = $1
        """,
        session_id,
    )
    if not session_row or session_row["id_tutor"] != tutor["id"]:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    if session_row["estado"] != "EN_CURSO":
        raise HTTPException(status_code=400, detail="Sesión ya finalizada")

    child_id = str(session_row["id_child"])
    level = session_row["nivel_sesion"]

    state_mgr = RedisStateManager(redis)
    sr_mgr = RedisSpacedRepManager(redis)

    bkt = await state_mgr.load_bkt_state(child_id)
    ctx = await state_mgr.load_session_context(child_id)
    if not bkt or not ctx:
        raise HTTPException(status_code=400, detail="Estado de sesión perdido, reinicia")

    # ── 1. STT ──
    transcript = ""
    if body.tipo_respuesta == "audio" and body.audio_base64:
        stt_result = await _stt.transcribe_base64(
            body.audio_base64,
            expected_text=body.texto_esperado,
        )
        transcript = stt_result.transcript
        is_low_conf = stt_result.is_low_confidence
    else:
        is_low_conf = False

    # ── 2. Metrics ──
    ipf = None
    if body.tipo_respuesta == "audio" and transcript and body.texto_esperado:
        ipf = compute_ipf(transcript, body.texto_esperado)
    elif body.tipo_respuesta == "seleccion" and body.id_seleccionado:
        ipf = 100.0 if body.id_seleccionado == body.texto_esperado else 0.0

    lme = None
    if transcript and level >= 2:
        lme = compute_lme(transcript)

    metrics = RawMetrics(
        tra_ms=body.tra_ms,
        ipf=ipf,
        lme=lme,
        is_low_confidence=is_low_conf,
        is_timeout=body.es_timeout,
    )

    # ── 3. Inference ──
    recent_emas = await state_mgr.get_session_emas(child_id)
    mastered = await _get_mastered_ids(UUID(child_id), db)

    sem_score = None
    if body.plantilla in ("Narrador", "Pensador") and transcript:
        from inference_engine.metrics.llm_evaluator import LLMEvaluator
        evaluator = LLMEvaluator(api_key=settings.gemini_api_key)
        sem_score = await evaluator.evaluate_narration(
            transcript, body.texto_esperado or "", level
        )

    decision = await evaluate_with_graph(
        metrics=metrics,
        bkt_state=bkt,
        session_context=ctx,
        navigator=navigator,
        mastered_ids=mastered,
        recent_emas=recent_emas,
        sem_score=sem_score,
    )

    # ── 4. Update session context ──
    if decision.action in (EngineAction.ADVANCE,):
        ctx.consecutive_correct += 1
        ctx.consecutive_errors = 0
    elif metrics.ipf is not None and metrics.ipf < 60:
        ctx.consecutive_errors += 1
        ctx.consecutive_correct = 0
    if body.es_timeout:
        ctx.consecutive_timeouts += 1
    ctx.exercises_done += 1

    await state_mgr.save_bkt_state(child_id, bkt)
    await state_mgr.save_session_context(child_id, ctx)

    if body.id_recurso:
        await state_mgr.mark_resource_used(child_id, body.id_recurso)

    # ── 5. Mastery persistence ──
    if bkt.is_mastered and body.id_hito:
        await db.execute(
            """
            INSERT INTO hito_mastery (id_child, id_hito, p_mastery, is_mastered, updated_at)
            VALUES ($1, $2, $3, TRUE, NOW())
            ON CONFLICT (id_child, id_hito) DO UPDATE
            SET p_mastery = EXCLUDED.p_mastery, is_mastered = TRUE, updated_at = NOW()
            """,
            UUID(child_id), body.id_hito, bkt.p_mastery,
        )
        if should_enqueue(bkt.p_mastery):
            await sr_mgr.enqueue_hito(child_id, body.id_hito)

    # ── 6. Log result ──
    await db.execute(
        """
        INSERT INTO resultados_ejercicio
            (id_sesion, id_recurso, id_hito, plantilla, hardware_req, lme, ipf, tra_ms, es_correcto, es_timeout)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
        session_id,
        body.id_recurso, body.id_hito, body.plantilla, "V-M",
        lme, ipf, body.tra_ms,
        decision.action == EngineAction.ADVANCE,
        body.es_timeout,
    )

    # ── 7. End session? ──
    if decision.action == EngineAction.END_SESSION:
        ipf_avg = await db.fetchval(
            "SELECT AVG(ipf) FROM resultados_ejercicio WHERE id_sesion = $1 AND ipf IS NOT NULL",
            session_id,
        )
        await db.execute(
            """
            UPDATE sesiones
            SET estado = 'COMPLETADA', fecha_fin = NOW(),
                ejercicios_completados = $1, ipf_promedio = $2
            WHERE id_sesion = $3
            """,
            ctx.exercises_done, round(float(ipf_avg or 0), 1), session_id,
        )
        await state_mgr.clear_session(child_id)
        await redis.delete(_sess_key(child_id))
        return {
            "estado_sesion": "COMPLETADA",
            "resumen_sesion": {
                "ejercicios_completados": ctx.exercises_done,
                "precision_promedio_ipf": round(float(ipf_avg or 0), 1),
            },
            "avatar_mensaje": "¡Lo hiciste increíble hoy! Descansa y mañana seguimos.",
        }

    next_hito_id = getattr(decision, "next_hito_id", None)
    return {
        "estado_sesion": "EN_CURSO",
        "decision_motor": {
            "accion": decision.action.value,
            "metricas": {
                "ipf": ipf,
                "lme": lme,
                "tra_ms": body.tra_ms,
                "p_maestria": round(bkt.p_mastery, 3),
            },
            "hardware_override": decision.hardware_override.value if decision.hardware_override else None,
        },
        "next_hito_id": next_hito_id,
        "avatar_mensaje": _avatar_message(decision.action),
    }


def _avatar_message(action: EngineAction) -> str:
    messages = {
        EngineAction.ADVANCE: "¡Excelente! ¡Lo lograste! Vamos al siguiente.",
        EngineAction.REPEAT: "¡Casi! Inténtalo una vez más.",
        EngineAction.HARDWARE_OVERRIDE: "¡Probemos de otra forma!",
        EngineAction.MINIGAME: "¡3 en fila! ¡Ganaste un juego especial!",
        EngineAction.LEVEL_DOWN: "Practiquemos un poco más esto.",
        EngineAction.END_SESSION: "¡Hasta mañana!",
    }
    return messages.get(action, "¡Sigue así!")


# ── GET /session/current/{child_id} ──

@router.get("/current/{child_id}")
async def get_current_session(child_id: UUID, tutor: CurrentTutor, db: DBConn, redis: RedisConn):
    child = await db.fetchrow(
        "SELECT id_child FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id, tutor["id"],
    )
    if not child:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    session_id = await redis.get(_sess_key(str(child_id)))
    if not session_id:
        return None  # 204 implicit

    session_id_str = session_id.decode() if isinstance(session_id, bytes) else session_id
    row = await db.fetchrow(
        "SELECT * FROM sesiones WHERE id_sesion = $1 AND estado = 'EN_CURSO'",
        UUID(session_id_str),
    )
    if not row:
        return None
    return dict(row)


# ── POST /session/{session_id}/end ──

@router.post("/{session_id}/end")
async def end_session(session_id: UUID, tutor: CurrentTutor, db: DBConn, redis: RedisConn):
    row = await db.fetchrow(
        """
        SELECT s.id_child FROM sesiones s
        JOIN children c ON c.id_child = s.id_child
        WHERE s.id_sesion = $1 AND c.id_tutor = $2 AND s.estado = 'EN_CURSO'
        """,
        session_id, tutor["id"],
    )
    if not row:
        raise HTTPException(status_code=404, detail="Sesión activa no encontrada")

    child_id = str(row["id_child"])
    ex_done = await db.fetchval(
        "SELECT COUNT(*) FROM resultados_ejercicio WHERE id_sesion = $1", session_id
    )

    await db.execute(
        "UPDATE sesiones SET estado = 'INTERRUMPIDA', fecha_fin = NOW(), ejercicios_completados = $1 WHERE id_sesion = $2",
        ex_done, session_id,
    )

    state_mgr = RedisStateManager(redis)
    await state_mgr.clear_session(child_id)
    await redis.delete(_sess_key(child_id))

    return {
        "session_id": str(session_id),
        "estado": "INTERRUMPIDA",
        "ejercicios_completados": ex_done,
        "datos_guardados": True,
    }
