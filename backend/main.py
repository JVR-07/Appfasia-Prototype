from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.lifespan import lifespan
from api.auth import router as auth_router
from api.children import router as children_router
from api.diagnostic import router as diagnostic_router
from api.session import router as session_router
from api.progress import router as progress_router
from api.chatbot import router as chatbot_router

app = FastAPI(
    title="Appfasia API",
    description="Motor de inferencia pedagógico para terapia de lenguaje infantil.",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"

app.include_router(auth_router,       prefix=f"{PREFIX}/auth",       tags=["Auth"])
app.include_router(children_router,   prefix=f"{PREFIX}/children",   tags=["Children"])
app.include_router(diagnostic_router, prefix=f"{PREFIX}/diagnostic", tags=["Diagnostic"])
app.include_router(session_router,    prefix=f"{PREFIX}/session",    tags=["Session"])
app.include_router(progress_router,   prefix=f"{PREFIX}/progress",   tags=["Progress"])
app.include_router(chatbot_router,    prefix=f"{PREFIX}/chatbot",    tags=["Chatbot"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "0.3.0"}
