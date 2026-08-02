from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Create the database engine using the DATABASE_URL from the .env file.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)


# Create a session factory for database operations.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Dependency used by FastAPI routes to get a database session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()