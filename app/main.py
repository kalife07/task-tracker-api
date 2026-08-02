# main.py - Application entry point.
# Creates the FastAPI instance, loads config, and registers all routers.
# Run with: uvicorn app.main:app --reload

from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.testing import router as testing_router

# Create the FastAPI application instance.
# The title and version appear in the auto-generated /docs (Swagger UI).
app = FastAPI(
    title="Task Tracker API",
    version="0.1.0",
description="A learning-focused REST API built with FastAPI and JSON file storage"
)

# Register routers.
# All routes defined in health_router are mounted at the root path.
# Add future routers here (e.g., tasks, projects) as the app grows.
app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(testing_router)


# Optional: log the active environment on startup so it's clear which
# .env values were loaded (helpful when switching between dev/prod configs).
@app.on_event("startup")
async def on_startup() -> None:
    print(f"[startup] APP_ENV={settings.app_env}  PORT={settings.port}")