import os
import sys
import pytest
from fastapi.testclient import TestClient

# Adjust import path to include root directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import SessionLocal, Base, engine
from seed_database import seed_database

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Fixture global: Membuat tabel database dan mengisinya dengan data ground-truth
    """
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    # Cleanup session resources if needed

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture session database per test function
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="module")
def api_client():
    """
    FastAPI TestClient Fixture
    """
    with TestClient(app) as client:
        yield client
