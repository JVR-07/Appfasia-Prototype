from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.dependencies import DBConn, CurrentTutor, ChildRow
import db.repositories.child_repo as child_repo

router = APIRouter()


class ChildCreate(BaseModel):
    nombre: str
    fecha_nac: date


class ChildUpdate(BaseModel):
    nombre: str | None = None
    fecha_nac: date | None = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_child(body: ChildCreate, tutor: CurrentTutor, db: DBConn):
    child = await child_repo.create(db, tutor["id"], body.nombre, body.fecha_nac)
    return child.to_dict()


@router.get("")
async def list_children(tutor: CurrentTutor, db: DBConn):
    children = await child_repo.list_by_tutor(db, tutor["id"])
    return [c.to_dict() for c in children]


@router.get("/{child_id}")
async def get_child(child: ChildRow, db: DBConn):
    child_id = child["id_child"]
    summary = await child_repo.get_bkt_summary(db, child_id)
    out = {k: (str(v) if isinstance(v, UUID) else v) for k, v in child.items()}
    out["bkt_summary"] = summary
    return out


@router.put("/{child_id}")
async def update_child(body: ChildUpdate, child: ChildRow, db: DBConn):
    child_id = child["id_child"]

    if body.nombre is not None:
        updated = await child_repo.update_nombre(db, child_id, body.nombre)
    elif body.fecha_nac is not None:
        updated = await child_repo.update_fecha_nac(db, child_id, body.fecha_nac)
    else:
        raise HTTPException(status_code=400, detail="Nada que actualizar")

    return updated.to_dict()
