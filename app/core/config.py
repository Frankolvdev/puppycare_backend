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

    # Database settings.
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()