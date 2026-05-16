import random
from dataclasses import dataclass, field
from enum import Enum

import asyncpg


class Plantilla(str, Enum):
    IMITADOR     = "Imitador"
    NOMBRADOR    = "Nombrador"
    IDENTIFICADOR = "Identificador"
    ORDENADOR    = "Ordenador"
    COMPLETADOR  = "Completador"
    CONSTRUCTOR  = "Constructor"
    NARRADOR     = "Narrador"
    PENSADOR     = "Pensador"

    @property
    def hardware_req(self) -> str:
        return _HARDWARE[self]

    @property
    def needs_llm_eval(self) -> bool:
        return self in (Plantilla.NARRADOR, Plantilla.PENSADOR)

    @property
    def needs_distractors(self) -> bool:
        return self in (Plantilla.IDENTIFICADOR,)


# Hardware mode per template
_HARDWARE: dict[Plantilla, str] = {
    Plantilla.IMITADOR:      "V-M",
    Plantilla.NOMBRADOR:     "V-M",
    Plantilla.IDENTIFICADOR: "T-S",
    Plantilla.ORDENADOR:     "T-A",
    Plantilla.COMPLETADOR:   "V-M",
    Plantilla.CONSTRUCTOR:   "T-A",
    Plantilla.NARRADOR:      "V-M",
    Plantilla.PENSADOR:      "V-M",
}

# Default thresholds per level
_UMBRALES: dict[int, dict] = {
    1: {"ipf_min": 70, "tra_max_ms": 6000, "timeouts_max": 3},
    2: {"ipf_min": 75, "tra_max_ms": 5000, "timeouts_max": 3},
    3: {"ipf_min": 80, "tra_max_ms": 4500, "timeouts_max": 2},
    4: {"ipf_min": 80, "tra_max_ms": 4000, "timeouts_max": 2},
    5: {"ipf_min": 85, "tra_max_ms": 4000, "timeouts_max": 2},
}


@dataclass
class ExercisePayload:
    id_actividad: str
    plantilla: Plantilla
    hardware_req: str
    id_recurso: str
    texto_esperado: str
    prompt: dict = field(default_factory=dict)
    opciones: list[dict] = field(default_factory=list)
    umbrales: dict = field(default_factory=dict)


class ContentEngine:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def pick_exercise(
        self,
        level: int,
        plantilla: Plantilla,
        used_resource_ids: set[str],
        id_hito: str | None = None,
    ) -> ExercisePayload | None:
        """Select an unused resource for the given level/template."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id_recurso, texto, imagen_url, audio_url
                FROM recursos
                WHERE nivel_sugerido = $1
                  AND ($2::text[] IS NULL OR id_recurso != ALL($2))
                ORDER BY RANDOM()
                LIMIT 1
                """,
                level,
                list(used_resource_ids) if used_resource_ids else None,
            )

        if not rows:
            return None

        row = dict(rows[0])
        hw = plantilla.hardware_req
        umbrales = _UMBRALES.get(level, _UMBRALES[1])

        prompt = self._build_prompt(plantilla, row)

        opciones: list[dict] = []
        if plantilla.needs_distractors:
            opciones = await self._pick_distractors(row["id_recurso"], level, count=2)
            correct_opt = {"id": row["id_recurso"], "imagen_url": row["imagen_url"]}
            opciones.insert(random.randint(0, len(opciones)), correct_opt)

        import uuid
        return ExercisePayload(
            id_actividad=f"ACT_{uuid.uuid4().hex[:6].upper()}",
            plantilla=plantilla,
            hardware_req=hw,
            id_recurso=row["id_recurso"],
            texto_esperado=row["texto"],
            prompt=prompt,
            opciones=opciones,
            umbrales=umbrales,
        )

    def _build_prompt(self, plantilla: Plantilla, row: dict) -> dict:
        match plantilla:
            case Plantilla.IMITADOR:
                return {"audio_url": row["audio_url"], "texto_estimulo": f"Di: {row['texto']}"}
            case Plantilla.NOMBRADOR:
                return {"imagen_url": row["imagen_url"], "texto_oculto": row["texto"]}
            case Plantilla.IDENTIFICADOR:
                return {"audio_url": row["audio_url"], "texto_estimulo": f"Toca: {row['texto']}"}
            case Plantilla.ORDENADOR:
                return {"imagen_url": row["imagen_url"], "instruccion": "Ordena las imágenes correctamente"}
            case Plantilla.COMPLETADOR:
                return {"imagen_url": row["imagen_url"], "frase_incompleta": f"El/La {row['texto']} es..."}
            case Plantilla.CONSTRUCTOR:
                return {"imagen_url": row["imagen_url"], "instruccion": "Construye una oración con estas palabras"}
            case Plantilla.NARRADOR:
                return {"imagen_url": row["imagen_url"], "instruccion": "Cuéntame lo que ves en esta imagen"}
            case Plantilla.PENSADOR:
                return {"imagen_url": row["imagen_url"], "instruccion": f"¿Qué sabes sobre {row['texto']}?"}
            case _:
                return {"imagen_url": row["imagen_url"]}

    async def _pick_distractors(
        self, correct_id: str, level: int, count: int = 2
    ) -> list[dict]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id_recurso, imagen_url FROM recursos
                WHERE nivel_sugerido = $1 AND id_recurso != $2
                ORDER BY RANDOM()
                LIMIT $3
                """,
                level, correct_id, count,
            )
        return [{"id": r["id_recurso"], "imagen_url": r["imagen_url"]} for r in rows]
