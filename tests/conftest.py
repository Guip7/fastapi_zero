from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch
from sqlalchemy.ext.asyncio import (create_async_engine, 
                                    AsyncSession
    )
import pytest_asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from ..fastapi_zero.settings import Settings
from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import User, table_registry
from fastapi_zero.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn: 
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def mock_db_time():
    @contextmanager
    def _mock_db_time(model):
        time = datetime(2026, 1, 1, 12, 0, 0)

        with patch("fastapi_zero.models.datetime") as mock_datetime:
            mock_datetime.now.return_value = time
            yield time

    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = "testtest"
    user = User(
        username="test",
        email="test@gmail.com",
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        "auth/token",
        data={"username": user.email, "password": user.clean_password},
    )
    return response.json()["access_token"]


@pytest.fixture
def settings():
    return Settings(
        DATABASE_URL="sqlite:///:memory:",
        SECRET_KEY="test-secret-key",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30
    )