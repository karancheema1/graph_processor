from pathlib import Path
from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import settings


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_migration_files() -> List[Path]:
    """Get all SQL migration files in order."""
    migrations_dir = Path(__file__).parent / 'migrations'
    return sorted(migrations_dir.glob('*.sql'))


def init_db() -> None:
    """Initialize database with both SQLAlchemy models and raw SQL migrations."""
    session = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        print("Created database tables from SQLAlchemy models")

        # Apply both sql migrations
        for migration_file in get_migration_files():
            print(f"Applying migration: {migration_file.name}")
            with migration_file.open('r') as f:
                sql = f.read()
                session.execute(text(sql))

        session.commit()
        print("Database initialization completed successfully")

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()


def ensure_db_initialized() -> None:
    """Ensure database is initialized with all required objects."""
    session = SessionLocal()
    try:
        # Check if graphs table exists
        result = session.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'graphs'
                )
            """)
        )
        tables_exist = result.scalar()

        if not tables_exist:
            print("Database tables not found. Initializing database...")
            init_db()
        else:
            print("Database tables already exist")

    except Exception as e:
        print(f"Error checking database state: {str(e)}")
        raise
    finally:
        session.close()


class DatabaseSession:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()