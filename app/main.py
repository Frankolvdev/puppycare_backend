from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import settings
from app.db.database import test_database_connection
from app.api.v1.endpoints.backoffice import router as backoffice_router
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Create the FastAPI application.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Enable cookie-based sessions for the backoffice.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.BACKOFFICE_SESSION_SECRET,
    same_site="lax",
    https_only=False,
)

# Register all API routes.
app.include_router(
    api_router,
    prefix="/api",
)

app.include_router(
    backoffice_router,
    prefix="/backoffice",
    tags=["Backoffice"],
)


@app.get("/", tags=["System"])
def root():
    """
    Root endpoint.
    """
    return {"message": f"{settings.APP_NAME} funcionando"}


@app.get("/health", tags=["System"])
def health_check():
    """
    API health check endpoint.
    """
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
    }


@app.get("/health/db", tags=["System"])
def database_health_check():
    """
    Database health check endpoint.
    """
    is_connected = test_database_connection()

    return {
        "database": "connected" if is_connected else "disconnected"
    }