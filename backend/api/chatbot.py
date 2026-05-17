from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.dependencies import DBConn, CurrentTutor, ChildRow
from services.chatbot_service import ChatbotService, ChildContext

router = APIRouter()
_chatbot = ChatbotService()


class ChatMessage(BaseModel):
    child_id: str
    mensaje: str
    modo: str = "consejos"
    historial: list[dict] = []


@router.post("/message")
async def chatbot_message(body: ChatMessage, tutor: CurrentTutor, db: DBConn):
    from uuid import UUID
    from db.repositories import child_repo, session_repo

    child_uuid = UUID(body.child_id)
    child_row = await child_repo.find_by_id_and_tutor(db, child_uuid, tutor["id"])
    if not child_row:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    summary = await child_repo.get_bkt_summary(db, child_uuid)
    
    ipf_avg = None
    sesiones_semana = None
    if body.modo == "resumenes":
        week_stats = await session_repo.get_weekly_stats(db, child_uuid)
        if week_stats:
            ipf_avg = float(week_stats["ipf_avg"]) if week_stats["ipf_avg"] else None
            sesiones_semana = week_stats["sesiones_completadas"]

    ctx = ChildContext(
        nombre=child_row.nombre,
        nivel_actual=child_row.nivel_actual,
        hitos_dominados=summary.get("hitos_dominados", 0),
        racha_dias=child_row.racha_dias,
        alertas=[],
        ipf_avg=ipf_avg,
        sesiones_semana=sesiones_semana
    )

    respuesta = await _chatbot.respond(body.mensaje, ctx, body.historial, body.modo)
    return {
        "respuesta": respuesta,
        "modelo_usado": "gemini-2.5-flash",
        "fuente_sugerida": None,
    }
