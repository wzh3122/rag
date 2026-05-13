from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_legal_qa import router as legal_qa_router
from app.config import get_settings
from app.db.database import init_db
from app.utils.rate_limit import RateLimitMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    init_db()

    app = FastAPI(
        title="Mainland Legal Agent RAG",
        version="1.0.0",
        description="China mainland legal multi-agent RAG backend skeleton.",
    )

    allow_origins = settings.frontend_cors_origins
    if settings.is_production and not allow_origins:
        allow_origins = []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)

    app.include_router(legal_qa_router)
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def index():
        return FileResponse(static_dir / "index.html")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
