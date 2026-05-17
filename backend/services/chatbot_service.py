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
    ipf_avg: float | None = None
    sesiones_semana: int | None = None


class ChatbotService:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)

    def _system_prompt(self, ctx: ChildContext, modo: str) -> str:
        nivel_desc = f"Nivel {ctx.nivel_actual}" if ctx.nivel_actual else "sin diagnóstico aún"
        alertas = "; ".join(ctx.alertas) if ctx.alertas else "Ninguna"
        
        base_context = (
            f"Contexto del niño/niña: {ctx.nombre}, {nivel_desc} de desarrollo del lenguaje. "
            f"Hitos dominados: {ctx.hitos_dominados}. Racha de días: {ctx.racha_dias}. "
            f"Alertas activas: {alertas}."
        )

        if modo == "consejos":
            return (
                f"Eres un asistente de terapia del lenguaje en la app Appfasia. Tu ROL EXCLUSIVO es dar consejos prácticos "
                f"al padre/cuidador para apoyar a {ctx.nombre} en casa, fuera de la app.\n\n"
                f"{base_context}\n\n"
                "REGLAS:\n"
                "- Responde de forma cálida, concisa y profesional.\n"
                "- Solo das consejos sobre estimulación del lenguaje, actividades en casa y refuerzo positivo.\n"
                "- Si el usuario pregunta algo fuera de este tema (ej. cómo funciona la app, datos del niño, temas generales), "
                "responde amablemente: 'Esa pregunta está fuera de mi especialidad. ¿Te gustaría que te sugiera una actividad para practicar en casa?'\n"
                "- Nunca des diagnósticos médicos."
            )
            
        elif modo == "dudas":
            return (
                f"Eres un asistente experto en la plataforma Appfasia. Tu ROL EXCLUSIVO es resolver dudas "
                f"técnicas y pedagógicas sobre los ejercicios, los niveles y la lógica de la app para {ctx.nombre}.\n\n"
                f"{base_context}\n\n"
                "REGLAS:\n"
                "- Responde de forma cálida, concisa y clara.\n"
                "- Explica por qué ciertos ejercicios se repiten, cómo funciona el sistema de niveles (BKT) y la importancia de los fonemas.\n"
                "- Si el usuario pregunta algo fuera de tema (ej. consejos de casa, temas médicos), responde: "
                "'Esa pregunta sale del ámbito de mis funciones. ¿Tienes alguna duda sobre los ejercicios o el progreso en la app?'"
            )
            
        elif modo == "resumenes":
            ipf = f"{ctx.ipf_avg}%" if ctx.ipf_avg is not None else "N/D"
            sesiones = ctx.sesiones_semana if ctx.sesiones_semana is not None else 0
            
            return (
                f"Eres un analista de progreso educativo en Appfasia. Tu ROL EXCLUSIVO es presentar métricas, resúmenes "
                f"y datos curiosos sobre el avance de {ctx.nombre}.\n\n"
                f"{base_context}\nIPF promedio reciente: {ipf}. Sesiones completadas esta semana: {sesiones}.\n\n"
                "REGLAS:\n"
                "- Presenta los datos de forma positiva, celebrando logros y motivando.\n"
                "- Usa analogías simples para las métricas si es necesario (ej. 'su precisión de {ipf} es como encestar 8 de cada 10 tiros').\n"
                "- Mantén la respuesta corta y alegre.\n"
                "- Si el usuario pregunta algo fuera de tema, responde: '¡Me encanta tu curiosidad! Pero mi especialidad es analizar "
                "el progreso. ¿Quieres que te cuente algo interesante sobre su avance reciente?'"
            )
            
        else:
            return "Eres un asistente de terapia del lenguaje. Responde de forma amigable."

    async def respond(
        self,
        message: str,
        child_context: ChildContext,
        historial: list[dict],
        modo: str
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
                    system_instruction=self._system_prompt(child_context, modo),
                    temperature=0.7,
                    max_output_tokens=800,
                ),
            )
            return response.text
        except Exception as e:
            # Fallback to smaller model
            try:
                response = await self._client.aio.models.generate_content(
                    model=FALLBACK_MODEL,
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=self._system_prompt(child_context, modo),
                    ),
                )
                return response.text
            except Exception as e2:
                return (
                    "Lo siento, el asistente no está disponible en este momento. "
                    "Por favor intenta de nuevo en unos minutos."
                )
