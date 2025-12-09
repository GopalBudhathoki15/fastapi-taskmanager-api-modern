# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from database import Base, get_db
from main import app

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine, expire_on_commit=False, autoflush=False
)


# Override get_db to use test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def test_client():
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    client = TestClient(app)
    yield client
    # Drop tables after tests
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def create_test_user(test_client):
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123",
    }

    response = test_client.post("/auth/register", json=payload)

    # If user already exists, fetch the user instead
    if response.status_code == 409:  # Conflict
        users_response = test_client.get("/users")
        user = next(u for u in users_response.json() if u["username"] == "alice")
    else:
        user = response.json()

    return user
