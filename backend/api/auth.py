from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from core.dependencies import DBConn, CurrentTutor
from core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_refresh_token,
)
from core.config import settings
import db.repositories.tutor_repo as tutor_repo

router = APIRouter()


# ── Request/Response models ──

class RegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.jwt_access_expire_minutes * 60


# ── Endpoints ──

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: DBConn):
    if await tutor_repo.find_by_email(db, body.email):
        raise HTTPException(status_code=409, detail="Email ya registrado")

    tutor = await tutor_repo.create(db, body.nombre, body.email, hash_password(body.password))
    return {"id_tutor": str(tutor.id), "nombre": tutor.nombre, "email": tutor.email}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DBConn):
    password_hash = await tutor_repo.get_password_hash(db, body.email)
    tutor = await tutor_repo.find_by_email(db, body.email)

    if tutor is None or password_hash is None or not verify_password(body.password, password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos")

    access = create_access_token(str(tutor.id))
    refresh = create_refresh_token(str(tutor.id))
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)

    await tutor_repo.store_refresh_token(db, tutor.id, sha256(refresh.encode()).hexdigest(), expires_at)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: DBConn):
    try:
        tutor_id_str = decode_refresh_token(body.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    token_hash = sha256(body.refresh_token.encode()).hexdigest()
    if not await tutor_repo.find_valid_refresh_token(db, UUID(tutor_id_str), token_hash):
        raise HTTPException(status_code=401, detail="Refresh token revocado o expirado")

    new_access = create_access_token(tutor_id_str)
    return {"access_token": new_access, "expires_in": settings.jwt_access_expire_minutes * 60}


@router.get("/me")
async def me(tutor: CurrentTutor):
    return tutor
