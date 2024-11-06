import pytest
from sqlalchemy import text
from src.db.database import Base, SessionLocal, engine


def cleanup_database(session):
    """Clean up test data from database."""
    try:
        # Delete all data but keep structure
        session.execute(text("TRUNCATE TABLE graphs CASCADE"))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


@pytest.fixture(scope="function")
def test_db():
    """
    Provide a clean database session for each test.
    Cleans up test data after each test.
    """
    session = SessionLocal()

    cleanup_database(session)

    try:
        with open('src/db/migrations/02_create_cycle_detection.sql', 'r') as f:
            session.execute(text(f.read()))
            session.commit()
    except Exception as e:
        # Function might already exist, which is fine
        session.rollback()

    yield session

    cleanup_database(session)
    session.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure database is properly set up before any tests run."""
    Base.metadata.create_all(bind=engine)

    # Create cycle detection function
    session = SessionLocal()
    try:
        with open('src/db/migrations/02_create_cycle_detection.sql', 'r') as f:
            session.execute(text(f.read()))
            session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

    yield