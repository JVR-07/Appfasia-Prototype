from dataclasses import dataclass

import google.genai as genai
from google.genai import types as genai_types

from core.config import settings

PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.5-flash-8b"


@dataclass
class ChildContext:
    nombre: str
    nivel_actual: int | None
    hitos_dominados: int
    racha_dias: int
    alertas: list[str]


class ChatbotService:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def _system_prompt(self, ctx: ChildContext) -> str:
        nivel_desc = (
            f"Nivel {ctx.nivel_actual}" if ctx.nivel_actual else "sin diagnóstico aún"
        )
        alertas = "; ".join(ctx.alertas) if ctx.alertas else "Ninguna"
        return (
            "Eres un asistente especializado en terapia del lenguaje infantil, "
            "entrenado para ayudar a padres y cuidadores. Respondes en español, "
            "con un tono cálido, empático y profesional. No realizas diagnósticos "
            "médicos, pero sí orientas sobre estrategias de estimulación en casa.\n\n"
            f"Contexto del niño/niña: {ctx.nombre}, {nivel_desc} de desarrollo del lenguaje. "
            f"Hitos dominados: {ctx.hitos_dominados}. Racha de días: {ctx.racha_dias}. "
            f"Alertas activas: {alertas}."
        )

    async def respond(
        self,
        message: str,
        child_context: ChildContext,
        historial: list[dict],
    ) -> str:
        contents = [
            genai_types.Content(
                role=turn["rol"],
                parts=[genai_types.Part(text=turn["contenido"])],
            )
            for turn in historial[-10:]  # Max 10 turns context
        ]
        contents.append(
            genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=message)],
            )
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=PRIMARY_MODEL,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    system_instruction=self._system_prompt(child_context),
                    temperature=0.7,
                    max_output_tokens=800,
                ),
            )
            return response.text
        except Exception:
            # Fallback to smaller model
            try:
                response = await self._client.aio.models.generate_content(
                    model=FALLBACK_MODEL,
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=self._system_prompt(child_context),
                    ),
                )
                return response.text
            except Exception as e:
                return (
                    "Lo siento, el asistente no está disponible en este momento. "
                    "Por favor intenta de nuevo en unos minutos."
                )
