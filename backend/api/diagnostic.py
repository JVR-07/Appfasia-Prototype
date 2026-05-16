import json
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.dependencies import DBConn, CurrentTutor, RedisConn
from inference_engine.diagnostic.evaluator import (
    DiagnosticState, evaluate_diagnostic_response, build_diagnostic_result,
    DIAGNOSTIC_MAX_INTERACTIONS,
)
from inference_engine.diagnostic.exercise_selector import (
    ExerciseRepository, select_diagnostic_exercise,
)

router = APIRouter()
_DIAG_TTL = 7200  # 2 hours


def _diag_key(session_id: str) -> str:
    return f"diag:{session_id}"


class StartRequest(BaseModel):
    child_id: str


class ResponseRequest(BaseModel):
    session_diag_id: str
    tipo_respuesta: str
    id_seleccionado: str | None = None
    tra_ms: int = 0
    audio_base64: str | None = None


@router.post("/start")
async def start_diagnostic(body: StartRequest, tutor: CurrentTutor, db: DBConn, redis: RedisConn):
    child_id = UUID(body.child_id)

    # Verify ownership
    child = await db.fetchrow(
        "SELECT * FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id, tutor["id"],
    )
    if not child:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    from datetime import date
    fecha_nac = child["fecha_nac"]
    today = date.today()
    edad_meses = (today.year - fecha_nac.year) * 12 + (today.month - fecha_nac.month)

    session_id = str(uuid4())
    engine = DiagnosticEngine()
    state = engine.start(edad_meses=edad_meses)

    await redis.setex(_diag_key(session_id), _DIAG_TTL, json.dumps(state))

    first_exercise = engine.get_exercise(state)
    return {
        "session_diag_id": session_id,
        "interaccion_num": 1,
        "max_interacciones": 15,
        "ejercicio": first_exercise,
        "avatar_mensaje": "¡Hola! Vamos a jugar un juego. ¿Listo?",
    }


@router.post("/response")
async def respond_diagnostic(body: ResponseRequest, tutor: CurrentTutor, db: DBConn, redis: RedisConn):
    raw = await redis.get(_diag_key(body.session_diag_id))
    if not raw:
        raise HTTPException(status_code=404, detail="Sesión diagnóstica no encontrada o expirada")

    state = json.loads(raw)
    engine = DiagnosticEngine()

    is_correct = body.id_seleccionado == state.get("correct_id")
    result = engine.step(state, correct=is_correct, tra_ms=body.tra_ms)

    if result["estado"] == "COMPLETADO":
        # Persist to DB
        child_id = UUID(state["child_id"])
        await db.execute(
            """
            UPDATE children
            SET nivel_actual = $1, diagnostico_ok = TRUE
            WHERE id_child = $2
            """,
            result["nivel_detectado"], child_id,
        )
        await db.execute(
            """
            INSERT INTO diagnosticos (id_child, nivel_detectado, total_interacciones, razon_finalizacion, historial_json)
            VALUES ($1, $2, $3, $4, $5)
            """,
            child_id, result["nivel_detectado"],
            result["resumen"]["total_interacciones"],
            result["resumen"]["razon"],
            json.dumps(state.get("historial", [])),
        )
        await redis.delete(_diag_key(body.session_diag_id))
    else:
        await redis.setex(_diag_key(body.session_diag_id), _DIAG_TTL, json.dumps(result["state"]))

    return result


@router.get("/result/{child_id}")
async def get_diagnostic_result(child_id: UUID, tutor: CurrentTutor, db: DBConn):
    child = await db.fetchrow(
        "SELECT id_child FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id, tutor["id"],
    )
    if not child:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    row = await db.fetchrow(
        """
        SELECT nivel_detectado, total_interacciones, razon_finalizacion, created_at
        FROM diagnosticos WHERE id_child = $1
        ORDER BY created_at DESC LIMIT 1
        """,
        child_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
    return dict(row)
