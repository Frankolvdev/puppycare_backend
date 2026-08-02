from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings.
    APP_NAME: str = "PuppyCare API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    GOOGLE_CLIENT_ID: str | None = None

    # Security settings.
    SECRET_KEY: str
    BACKOFFICE_SESSION_SECRET: str
    SESSION_HTTPS_ONLY: bool = False

    # Database settings.
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE_SECONDS: int = 1800

    # Persistent file storage.
    # Locally this can remain "uploads". In AWS ECS/Fargate, mount EFS at
    # /app/uploads and set UPLOAD_DIR=/app/uploads.
    UPLOAD_DIR: str = "uploads"

    # Container startup behavior.
    RUN_DB_MIGRATIONS: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
