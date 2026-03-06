from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from src.api.middleware import register_exception_handlers, register_middleware
from src.api.v1.router import api_router
from src.shared.infrastructure.database import engine
from src.shared.infrastructure.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    yield
    # Shutdown
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Marketing Automation API",
        description="Campaign Creator MVP — define audiences, rules, and simulate performance.",
        version="0.1.0",
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
