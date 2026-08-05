import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError
from config import settings

logger = logging.getLogger(__name__)

def create_db_engine():
    """
    Membuat SQLAlchemy Engine dengan PostgreSQL utama, dan automatic fallback ke SQLite jika PostgreSQL offline
    """
    try:
        pg_engine = create_engine(
            settings.DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        # Test connection
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Terhubung ke PostgreSQL Database: {settings.POSTGRES_DB}")
        return pg_engine
    except Exception as e:
        logger.warning(f"PostgreSQL tidak dapat diakses ({e}). Menggunakan SQLite Local Database Fallback.")
        sqlite_db_path = os.path.join(os.path.dirname(__file__), "kideco_fuel_ratio.db")
        sqlite_url = f"sqlite:///{sqlite_db_path}"
        sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        return sqlite_engine

engine = create_db_engine()

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Model Class
class Base(DeclarativeBase):
    pass

def get_db():
    """
    Dependency generator untuk FastAPI endpoint (Session management per request)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> dict:
    """
    Memeriksa status koneksi database
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.scalar()
            return {
                "status": "connected",
                "engine": str(engine.url.drivername),
                "database": settings.POSTGRES_DB if "postgresql" in str(engine.url) else "sqlite_local"
            }
    except OperationalError as e:
        logger.error(f"Gagal terhubung ke database: {str(e)}")
        return {
            "status": "disconnected",
            "error": str(e)
        }
