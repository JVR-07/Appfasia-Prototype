from dataclasses import dataclass, field
from enum import Enum


class EdgeType(str, Enum):
    REQUIERE_DE = "REQUIERE_DE"
    PRECEDE_A = "PRECEDE_A"
    RUTA_ALTERNATIVA = "RUTA_ALTERNATIVA"
    REFUERZA = "REFUERZA"


class HitoDimension(str, Enum):
    EXPRESIVO = "expresivo"
    COMPRENSIVO = "comprensivo"
    FONOLOGICO = "fonologico"
    LECTURA = "lectura"
    PRAGMATICO = "pragmatico"
    SEMANTICO = "semantico"


# Node representation
@dataclass
class HitoNode:
    id_hito: str
    nombre: str
    nivel: int
    rango_edad_min: int
    rango_edad_max: int
    dimension: HitoDimension
    es_bloqueante: bool
    orden_interno: int

# Query result types
@dataclass
class GraphRoute:
    next_hito: HitoNode
    blocked_by: list[str] = field(default_factory=list)
    alternative_route: str | None = None

# Detected learning gap
@dataclass
class LagTicket:
    child_level: int
    lag_hito_id: str
    lag_level: int
    recovery_hitos: list[str] = field(default_factory=list)
