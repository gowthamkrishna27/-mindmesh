"""Health check endpoint for MindMesh backend."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="System Health Check")
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Check API and database connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {type(e).__name__}"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "database": db_status,
                "environment": settings.ENVIRONMENT,
                "version": "3.0.0",
            },
        )

    return {
        "status": "ok",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "version": "3.0.0",
    }
