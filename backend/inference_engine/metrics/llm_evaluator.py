import json
from typing import Optional

import google.genai as genai
from google.genai import types as genai_types

from inference_engine.schemas import SEMScore

PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.5-flash-8b"
SEM_MASTERY_THRESHOLD = 70.0


class LLMEvaluator:
    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    async def evaluate_narration(
        self, transcript: str, exercise_context: str, level: int
    ) -> SEMScore:
        prompt = self._build_prompt("narration", transcript, exercise_context, level)
        return await self._call_llm(prompt, "narration")

    async def evaluate_open_response(
        self, transcript: str, exercise_context: str, level: int
    ) -> SEMScore:
        prompt = self._build_prompt("open_response", transcript, exercise_context, level)
        return await self._call_llm(prompt, "open_response")

    def _build_prompt(
        self, rubric_type: str, transcript: str, context: str, level: int
    ) -> str:
        if rubric_type == "narration":
            return (
                f"Evalúa la siguiente narración de un niño en nivel {level} de terapia de lenguaje.\n"
                f"Contexto del ejercicio: {context}\n"
                f"Transcripción: '{transcript}'\n\n"
                "Proporciona una evaluación en formato JSON estricto con las siguientes claves:\n"
                "- score_global: número del 0 al 100 (promedio ponderado).\n"
                "- dimensions: objeto con claves 'coherencia', 'vocabulario', 'secuencia' (valores 0-100).\n"
            )
        return (
            f"Evalúa la siguiente respuesta de un niño en nivel {level} de terapia de lenguaje.\n"
            f"Contexto de la pregunta: {context}\n"
            f"Transcripción: '{transcript}'\n\n"
            "Proporciona una evaluación en formato JSON estricto con las siguientes claves:\n"
            "- score_global: número del 0 al 100 (promedio ponderado).\n"
            "- dimensions: objeto con claves 'relevancia', 'claridad', 'vocabulario' (valores 0-100).\n"
        )

    async def _call_llm(self, prompt: str, rubric_type: str) -> SEMScore:
        try:
            config = genai_types.GenerateContentConfig(
                response_mime_type="application/json"
            )
            try:
                response = await self._client.aio.models.generate_content(
                    model=PRIMARY_MODEL,
                    contents=prompt,
                    config=config,
                )
            except Exception:
                # Fallback
                response = await self._client.aio.models.generate_content(
                    model=FALLBACK_MODEL,
                    contents=prompt,
                    config=config,
                )

            data = json.loads(response.text)
            return SEMScore(
                score_global=float(data.get("score_global", 0)),
                dimensions=data.get("dimensions", {}),
                rubric_type=rubric_type,
            )
        except Exception as e:
            print(f"LLM evaluation failed: {e}")
            return SEMScore(
                score_global=0.0,
                dimensions={},
                rubric_type=rubric_type,
                is_available=False,
            )
