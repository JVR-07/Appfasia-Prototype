from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.dependencies import DBConn, CurrentTutor, ChildRow
from services.chatbot_service import ChatbotService, ChildContext

router = APIRouter()
_chatbot = ChatbotService()


class ChatMessage(BaseModel):
    child_id: str
    mensaje: str
    historial: list[dict] = []


@router.post("/message")
async def chatbot_message(body: ChatMessage, tutor: CurrentTutor, db: DBConn):
    from uuid import UUID

    # Load child and verify ownership
    child_row = await db.fetchrow(
        "SELECT * FROM children WHERE id_child = $1 AND id_tutor = $2",
        UUID(body.child_id), tutor["id"],
    )
    if not child_row:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    # Load BKT summary
    summary = await db.fetchrow(
        "SELECT COUNT(*) FILTER (WHERE is_mastered) AS dominados FROM hito_mastery WHERE id_child = $1",
        UUID(body.child_id),
    )

    ctx = ChildContext(
        nombre=child_row["nombre"],
        nivel_actual=child_row["nivel_actual"],
        hitos_dominados=summary["dominados"] if summary else 0,
        racha_dias=child_row.get("racha_dias", 0),
        alertas=[],
    )

    respuesta = await _chatbot.respond(body.mensaje, ctx, body.historial)
    return {
        "respuesta": respuesta,
        "modelo_usado": "gemini-2.5-flash",
        "fuente_sugerida": None,
    }
