from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes.publish import router as publish_router
from app.routes.webhook import router as webhook_router
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info("서버 시작 | env=%s | model=%s", settings.env, settings.openai_model)
    yield
    logger.info("서버 종료")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Instagram AI Agent",
        description="Instagram 댓글 자동 응답 MVP",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(webhook_router)
    app.include_router(publish_router)

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "env": settings.env}

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("처리되지 않은 예외 | path=%s | error=%s", request.url.path, str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()
