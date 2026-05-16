"""
Typed row dataclasses for PostgreSQL tables.
These are the Python representations of DB rows — used across repos and routers.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class TutorRow:
    id: UUID
    nombre: str
    email: str
    created_at: datetime

    @classmethod
    def from_record(cls, r) -> TutorRow:
        return cls(
            id=r["id"],
            nombre=r["nombre"],
            email=r["email"],
            created_at=r["created_at"],
        )


@dataclass(frozen=True)
class ChildRow:
    id_child: UUID
    id_tutor: UUID
    nombre: str
    fecha_nac: date
    nivel_actual: int | None
    diagnostico_ok: bool
    racha_dias: int
    created_at: datetime

    @classmethod
    def from_record(cls, r) -> ChildRow:
        return cls(
            id_child=r["id_child"],
            id_tutor=r["id_tutor"],
            nombre=r["nombre"],
            fecha_nac=r["fecha_nac"],
            nivel_actual=r["nivel_actual"],
            diagnostico_ok=r["diagnostico_ok"],
            racha_dias=r.get("racha_dias") or 0,
            created_at=r["created_at"],
        )

    def edad_meses(self) -> int:
        today = date.today()
        months = (today.year - self.fecha_nac.year) * 12 + (today.month - self.fecha_nac.month)
        if today.day < self.fecha_nac.day:
            months -= 1
        return max(0, months)

    def to_dict(self) -> dict:
        return {
            "id_child": str(self.id_child),
            "id_tutor": str(self.id_tutor),
            "nombre": self.nombre,
            "fecha_nac": str(self.fecha_nac),
            "edad_meses": self.edad_meses(),
            "nivel_actual": self.nivel_actual,
            "diagnostico_ok": self.diagnostico_ok,
            "racha_dias": self.racha_dias,
        }


@dataclass(frozen=True)
class SessionRow:
    id_sesion: UUID
    id_child: UUID
    nivel_sesion: int
    estado: str
    ejercicios_completados: int
    ipf_promedio: float | None

    @classmethod
    def from_record(cls, r) -> SessionRow:
        return cls(
            id_sesion=r["id_sesion"],
            id_child=r["id_child"],
            nivel_sesion=r["nivel_sesion"],
            estado=r["estado"],
            ejercicios_completados=r.get("ejercicios_completados") or 0,
            ipf_promedio=r.get("ipf_promedio"),
        )


@dataclass(frozen=True)
class HitoMasteryRow:
    id_child: UUID
    id_hito: str
    p_mastery: float
    is_mastered: bool

    @classmethod
    def from_record(cls, r) -> HitoMasteryRow:
        return cls(
            id_child=r["id_child"],
            id_hito=r["id_hito"],
            p_mastery=r["p_mastery"],
            is_mastered=r["is_mastered"],
        )
