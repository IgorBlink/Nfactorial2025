import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db, Base
from src.models import User, TaskDB

# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to" in response.json()["message"]


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_login_user():
    # First register a user
    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpassword123"
        }
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        data={
            "username": "loginuser",
            "password": "loginpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_protected_endpoint_without_token():
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_create_task_without_auth():
    response = client.post(
        "/tasks/create_task",
        json={
            "title": "Test Task",
            "description": "Test Description"
        }
    )
    assert response.status_code == 401


class TestWithAuth:
    def setup_method(self):
        # Register and login to get token
        client.post(
            "/auth/register",
            json={
                "username": "authuser",
                "email": "auth@example.com",
                "password": "authpassword123"
            }
        )
        
        response = client.post(
            "/auth/login",
            data={
                "username": "authuser",
                "password": "authpassword123"
            }
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_user_info(self):
        response = client.get("/auth/me", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "authuser"
    
    def test_create_task(self):
        response = client.post(
            "/tasks/create_task",
            json={
                "title": "Test Task",
                "description": "Test Description"
            },
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["completed"] == False
    
    def test_get_tasks(self):
        # Create a task first
        client.post(
            "/tasks/create_task",
            json={
                "title": "Another Task",
                "description": "Another Description"
            },
            headers=self.headers
        )
        
        response = client.get("/tasks/get_tasks", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1 