"""API routes module."""

from fastapi import APIRouter
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.educators import router as educators_router
from app.api.routes.health import router as health_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.students import router as students_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(educators_router)
api_router.include_router(admin_router)
api_router.include_router(sessions_router)
api_router.include_router(students_router)
