from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from core.dependencies import DBConn
from db.repositories import publications_repo

router = APIRouter()

@router.get("")
async def get_publications(db: DBConn, since: str | None = None):
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            return await publications_repo.get_publications_since(db, since_dt)
        except ValueError:
            return await publications_repo.get_all_publications(db)
    return await publications_repo.get_all_publications(db)

@router.get("/{pub_id}")
async def get_publication(pub_id: UUID, db: DBConn):
    pub = await publications_repo.get_publication_by_id(db, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return pub
