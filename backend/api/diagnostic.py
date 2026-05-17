import json
from uuid import UUID, uuid4
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from core.dependencies import DBConn, CurrentTutor, RedisConn
from inference_engine.diagnostic.evaluator import (
    evaluate_diagnostic_response, DiagnosticResponse,
)
from inference_engine.diagnostic.state_machine import DiagnosticState
from inference_engine.diagnostic.exercise_selector import (
    ExerciseRepository, select_diagnostic_exercise,
)
from inference_engine.diagnostic.result_calculator import build_diagnostic_result
from inference_engine.diagnostic.level_calculator import expected_level, start_level
from inference_engine.schemas import DiagnosticPhase, DiagnosticDifficulty
from inference_engine.rules.constants import DIAGNOSTIC_MAX_INTERACTIONS

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
    is_correct: bool | None = None



class PgExerciseRepo:
    """Implements ExerciseRepository protocol using PostgreSQL."""

    def __init__(self, conn):
        self._conn = conn

    async def fetch_resource(self, level: int, difficulty: DiagnosticDifficulty, exclude_ids: list[str]) -> dict:
        row = await self._conn.fetchrow(
            """
            SELECT id_recurso, texto, imagen_url, audio_url, nivel_sugerido
            FROM recursos
            WHERE nivel_sugerido = $1
              AND ($2::text[] IS NULL OR id_recurso != ALL($2))
            ORDER BY RANDOM()
            LIMIT 1
            """,
            level,
            exclude_ids if exclude_ids else None,
        )
        if not row:
            raise HTTPException(status_code=500, detail=f"No hay recursos disponibles para nivel {level}")
        return dict(row)

    async def fetch_distractors(self, level: int, correct_id: str, exclude_ids: list[str], count: int = 2) -> list[dict]:
        rows = await self._conn.fetch(
            """
            SELECT id_recurso, texto, imagen_url, audio_url
            FROM recursos
            WHERE nivel_sugerido = $1
              AND id_recurso != $2
              AND ($3::text[] IS NULL OR id_recurso != ALL($3))
            ORDER BY RANDOM()
            LIMIT $4
            """,
            level, correct_id,
            exclude_ids if exclude_ids else None,
            count,
        )
        return [dict(r) for r in rows]



def _serialize_state(state: DiagnosticState) -> str:
    d = asdict(state)
    d["phase"] = state.phase.value
    d["current_difficulty"] = state.current_difficulty.value
    for h in d["history"]:
        h["difficulty"] = h["difficulty"].value if hasattr(h["difficulty"], "value") else h["difficulty"]
    return json.dumps(d)


def _deserialize_state(raw: str) -> DiagnosticState:
    d = json.loads(raw)
    from inference_engine.diagnostic.state_machine import DiagnosticInteraction
    d["phase"] = DiagnosticPhase(d["phase"])
    d["current_difficulty"] = DiagnosticDifficulty(d["current_difficulty"])
    d["history"] = [
        DiagnosticInteraction(
            interaction_num=h["interaction_num"],
            level=h["level"],
            difficulty=DiagnosticDifficulty(h["difficulty"]),
            resource_id=h["resource_id"],
            correct=h["correct"],
            tra_ms=h["tra_ms"],
            is_timeout=h["is_timeout"],
        )
        for h in d["history"]
    ]
    return DiagnosticState(**d)


def _exercise_to_frontend(exercise, state: DiagnosticState) -> dict:
    """Transform the backend ActivityInstance into the frontend-expected format."""
    options = []
    for opt in exercise.options:
        options.append({
            "id": opt["id_recurso"],
            "texto": opt.get("texto", ""),
            "imagen_url": opt.get("imagen_url", ""),
        })

    tipo_interaccion = "seleccion"
    if exercise.hardware_req == "M-A" or exercise.hardware_req == "T-A":
        tipo_interaccion = "audio"

    consigna = "Responde"
    if tipo_interaccion == "seleccion" and options:
        consigna = f"Toca: {options[0]['texto']}"
    elif tipo_interaccion == "audio":
        consigna = "¿Qué es esto? Dilo en voz alta"

    return {
        "id_recurso": exercise.correct_resource_id,
        "plantilla": exercise.template,
        "hardware_req": exercise.hardware_req,
        "tipo_interaccion": tipo_interaccion,
        "consigna": consigna,
        "texto_esperado": exercise.correct_resource_id,
        "imagen_url": exercise.options[0].get("imagen_url", "") if exercise.options else "",
        "opciones": options,
    }


@router.post("/start")
async def start_diagnostic(body: StartRequest, tutor: CurrentTutor, db: DBConn, redis: RedisConn):
    child_id = UUID(body.child_id)

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
    exp_lvl = expected_level(edad_meses)
    init_level, init_difficulty = start_level(exp_lvl)

    state = DiagnosticState(
        session_diag_id=session_id,
        child_id=str(child_id),
        phase=DiagnosticPhase.AWAITING_BASAL,
        interaction_num=1,
        current_test_level=init_level,
        current_difficulty=init_difficulty,
    )

    repo = PgExerciseRepo(db)
    exercise = await select_diagnostic_exercise(
        repo, state.current_test_level, state.current_difficulty, state.used_items,
    )

    await redis.setex(_diag_key(session_id), _DIAG_TTL, _serialize_state(state))
    correct_key = f"diag:correct:{session_id}"
    await redis.setex(correct_key, _DIAG_TTL, exercise.correct_resource_id)

    return {
        "session_diag_id": session_id,
        "interaccion_num": 1,
        "max_interacciones": DIAGNOSTIC_MAX_INTERACTIONS,
        "ejercicio": _exercise_to_frontend(exercise, state),
        "avatar_mensaje": "¡Hola! Vamos a jugar un juego. ¿Listo?",
    }


@router.post("/response")
async def respond_diagnostic(body: ResponseRequest, tutor: CurrentTutor, db: DBConn, redis: RedisConn):
    raw = await redis.get(_diag_key(body.session_diag_id))
    if not raw:
        raise HTTPException(status_code=404, detail="Sesión diagnóstica no encontrada o expirada")

    state = _deserialize_state(raw.decode() if isinstance(raw, bytes) else raw)

    correct_key = f"diag:correct:{body.session_diag_id}"
    correct_raw = await redis.get(correct_key)
    correct_id = correct_raw.decode() if isinstance(correct_raw, bytes) else (correct_raw or "")

    response = DiagnosticResponse(
        selected_id=body.id_seleccionado or "",
        correct_id=correct_id,
        tra_ms=body.tra_ms,
        is_timeout=(body.tra_ms > 10000),
        is_correct_override=body.is_correct,
    )

    step_result = evaluate_diagnostic_response(state, response)

    if step_result.phase == DiagnosticPhase.COMPLETED:
        diag_result = step_result.diagnostic_result
        child_id = UUID(state.child_id)
        nivel = diag_result["detected_level"]

        await db.execute(
            "UPDATE children SET nivel_actual = $1, diagnostico_ok = TRUE WHERE id_child = $2",
            nivel, child_id,
        )
        await db.execute(
            """
            INSERT INTO diagnosticos (id_child, nivel_detectado, total_interacciones, razon_finalizacion, historial_json)
            VALUES ($1, $2, $3, $4, $5)
            """,
            child_id, nivel,
            diag_result["total_interactions"],
            diag_result["exit_reason"].value if hasattr(diag_result["exit_reason"], "value") else str(diag_result["exit_reason"]),
            json.dumps([]),
        )

        await redis.delete(_diag_key(body.session_diag_id))
        await redis.delete(correct_key)

        nivel_desc = {
            1: "Descubrimiento Lingüístico (0-2 años)",
            2: "Estructuración Telegráfica (2-4 años)",
            3: "Consolidación Sintáctica (4-6 años)",
            4: "Competencia Metalingüística (6-8 años)",
            5: "Razonamiento Abstracto (8-11 años)",
        }.get(nivel, "No determinado")

        return {
            "estado": "COMPLETADO",
            "nivel_detectado": nivel,
            "descripcion_nivel": nivel_desc,
            "avatar_mensaje": "¡Lo hiciste genial! Ya sé cómo podemos jugar juntos.",
            "resumen": {
                "total_interacciones": diag_result["total_interactions"],
                "razon": diag_result["exit_reason"].value if hasattr(diag_result["exit_reason"], "value") else str(diag_result["exit_reason"]),
            },
        }

    repo = PgExerciseRepo(db)
    next_exercise = await select_diagnostic_exercise(
        repo, state.current_test_level, state.current_difficulty, state.used_items,
    )

    await redis.setex(_diag_key(body.session_diag_id), _DIAG_TTL, _serialize_state(state))
    await redis.setex(correct_key, _DIAG_TTL, next_exercise.correct_resource_id)

    return {
        "estado": "EN_CURSO",
        "interaccion_num": state.interaction_num,
        "max_interacciones": DIAGNOSTIC_MAX_INTERACTIONS,
        "siguiente_ejercicio": _exercise_to_frontend(next_exercise, state),
        "avatar_mensaje": "¡Muy bien! Siguiente...",
    }


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
