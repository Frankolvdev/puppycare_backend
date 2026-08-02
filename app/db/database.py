from sqlalchemy import text

from app.db.session import engine


# Simple function to test the database connection.
def test_database_connection() -> bool:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar() == 1