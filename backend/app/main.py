"""MindMesh FastAPI Application Entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.errors import register_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context for startup and shutdown hooks."""
    yield


def create_application() -> FastAPI:
    """Application factory for MindMesh backend."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="3.0.0",
        description="MindMesh Backend: Adaptive Learning Dependency Graph (v3.0)",
        docs_url="/docs" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # Register standardized error handlers (v3 Section 11.13)
    register_error_handlers(app)

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes: both /health directly and /api/v1 prefix
    app.include_router(health_router, prefix="", tags=["Health"])
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
