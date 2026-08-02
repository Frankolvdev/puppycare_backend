from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Create the database engine using the DATABASE_URL from the environment.
# pool_pre_ping avoids returning stale RDS connections after network changes
# or database maintenance.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
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
