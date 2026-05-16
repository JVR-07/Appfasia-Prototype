import json
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.dependencies import DBConn, CurrentTutor, RedisConn

router = APIRouter()


class LabelRequest(BaseModel):
    etiqueta: str
    nota: str | None = None


class ExternalAdvanceRequest(BaseModel):
    descripcion: str
    id_hito_relacionado: str


@router.get("/{child_id}")
async def get_progress(child_id: UUID, tutor: CurrentTutor, db: DBConn):
    child = await db.fetchrow(
        "SELECT * FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id, tutor["id"],
    )
    if not child:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    # Week summary
    week = await db.fetchrow(
        """
        SELECT
            COUNT(*) AS sesiones_completadas,
            COALESCE(SUM(EXTRACT(EPOCH FROM (fecha_fin - fecha_inicio)) / 60)::INT, 0) AS minutos_totales,
            COALESCE(SUM(hitos_dominados_hoy), 0) AS hitos_dominados
        FROM sesiones
        WHERE id_child = $1
          AND estado = 'COMPLETADA'
          AND fecha_inicio >= NOW() - INTERVAL '7 days'
        """,
        child_id,
    )

    # IPF average last week
    ipf_row = await db.fetchrow(
        """
        SELECT ROUND(AVG(ipf_promedio)::numeric, 1) AS ipf_avg
        FROM sesiones
        WHERE id_child = $1 AND estado = 'COMPLETADA'
          AND fecha_inicio >= NOW() - INTERVAL '7 days'
        """,
        child_id,
    )

    # Lag alerts
    mastery_row = await db.fetchrow(
        "SELECT COUNT(*) FILTER (WHERE is_mastered) AS dominados FROM hito_mastery WHERE id_child = $1",
        child_id,
    )

    nivel = child["nivel_actual"]
    nivel_desc = {
        1: "Descubrimiento Lingüístico (0-2 años)",
        2: "Estructuración Telegráfica (2-4 años)",
        3: "Consolidación Sintáctica (4-6 años)",
        4: "Competencia Metalingüística (6-8 años)",
        5: "Razonamiento Abstracto (8-11 años)",
    }.get(nivel, "No determinado")

    return {
        "child_id": str(child_id),
        "nombre": child["nombre"],
        "nivel_actual": nivel,
        "descripcion_nivel": nivel_desc,
        "racha_dias": child.get("racha_dias", 0),
        "resumen_semana": dict(week),
        "metricas_traducidas": {
            "precision_habla": f"IPF promedio: {ipf_row['ipf_avg'] or 'N/D'}%",
            "hitos_dominados_total": mastery_row["dominados"],
        },
        "alertas": [],
    }


@router.get("/{child_id}/sessions")
async def get_sessions(child_id: UUID, tutor: CurrentTutor, db: DBConn, limit: int = 10, offset: int = 0):
    child = await db.fetchrow(
        "SELECT id_child FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id, tutor["id"],
    )
    if not child:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    total = await db.fetchval("SELECT COUNT(*) FROM sesiones WHERE id_child = $1", child_id)
    rows = await db.fetch(
        """
        SELECT id_sesion, fecha_inicio, estado, ejercicios_completados, ipf_promedio, etiqueta_tutor
        FROM sesiones
        WHERE id_child = $1
        ORDER BY fecha_inicio DESC
        LIMIT $2 OFFSET $3
        """,
        child_id, limit, offset,
    )
    return {"total": total, "sessions": [dict(r) for r in rows]}


@router.post("/{child_id}/sessions/{session_id}/label")
async def label_session(
    child_id: UUID, session_id: UUID,
    body: LabelRequest, tutor: CurrentTutor, db: DBConn,
):
    valid_labels = {"Cansancio", "Distracción", "Enfermedad", "Otro"}
    if body.etiqueta not in valid_labels:
        raise HTTPException(status_code=400, detail=f"Etiqueta inválida. Opciones: {valid_labels}")

    # Verify ownership
    row = await db.fetchrow(
        """
        SELECT s.id_sesion FROM sesiones s
        JOIN children c ON c.id_child = s.id_child
        WHERE s.id_sesion = $1 AND c.id_tutor = $2
        """,
        session_id, tutor["id"],
    )
    if not row:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    # Adjust r0 weight: flagged sessions have less impact on EMA
    r0 = {"Enfermedad": 0.1, "Cansancio": 0.2, "Distracción": 0.3, "Otro": 0.4}[body.etiqueta]
    await db.execute(
        "UPDATE sesiones SET etiqueta_tutor = $1, r0_weight = $2 WHERE id_sesion = $3",
        body.etiqueta, r0, session_id,
    )
    return {
        "session_id": str(session_id),
        "etiqueta": body.etiqueta,
        "r0_weight_ajustado": r0,
        "mensaje": "El rendimiento de esta sesión tendrá menos peso en el cálculo del progreso.",
    }


@router.post("/{child_id}/external-advance")
async def external_advance(
    child_id: UUID, body: ExternalAdvanceRequest, tutor: CurrentTutor, db: DBConn, redis: RedisConn,
):
    child = await db.fetchrow(
        "SELECT id_child FROM children WHERE id_child = $1 AND id_tutor = $2",
        child_id, tutor["id"],
    )
    if not child:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    # Schedule verification in next session via Redis (TTL 7 days)
    key = f"ext_advance:{child_id}"
    await redis.setex(key, 7 * 86400, json.dumps({
        "id_hito": body.id_hito_relacionado,
        "descripcion": body.descripcion,
    }))
    return {
        "mensaje": "¡Excelente noticia! Hemos programado una prueba de verificación para la próxima sesión.",
        "prueba_verificacion_programada": True,
    }
