from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.router import router as api_router
from app.api.v1.endpoints.backoffice import router as backoffice_router
from app.core.config import settings
from app.db.database import test_database_connection


# Create the FastAPI application.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


# The directory can be backed by an Amazon EFS mount in production.
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=str(upload_dir)),
    name="uploads",
)


# Enable cookie-based sessions for the backoffice.
# SESSION_HTTPS_ONLY must be true when the service is exposed through HTTPS.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.BACKOFFICE_SESSION_SECRET,
    same_site="lax",
    https_only=settings.SESSION_HTTPS_ONLY,
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
    return {"message": f"{settings.APP_NAME} funcionando"}


@app.get("/health", tags=["System"])
def health_check():
    # This endpoint intentionally does not query PostgreSQL. AWS can use it
    # as the container/load-balancer health check even while RDS is starting.
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
    }


@app.get("/health/db", tags=["System"])
def database_health_check():
    is_connected = test_database_connection()

    return {
        "database": "connected" if is_connected else "disconnected"
    }
