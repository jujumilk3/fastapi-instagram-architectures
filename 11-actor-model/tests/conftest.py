from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from actor_model.actors.registry import ActorRegistry
from actor_model.api.dependencies import get_registry
from actor_model.main import app, create_registry
from actor_model.models.base import Base

TEST_DB_URL = "sqlite+aiosqlite:///./test_actor_model.db"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

_registry: ActorRegistry | None = None


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def setup_db():
    global _registry

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _registry = create_registry(db_factory=test_session)
    await _registry.start_all()

    app.dependency_overrides[get_registry] = lambda: _registry

    yield

    await _registry.stop_all()
    _registry = None

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(loop_scope="session")
async def auth_client(client: AsyncClient) -> AsyncClient:
    await client.post("/api/auth/register", json={
        "username": "testuser", "email": "test@example.com", "password": "password123", "full_name": "Test User"
    })
    resp = await client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture(loop_scope="session")
async def second_user_token(client: AsyncClient) -> str:
    await client.post("/api/auth/register", json={
        "username": "otheruser", "email": "other@example.com", "password": "password123"
    })
    resp = await client.post("/api/auth/login", json={"email": "other@example.com", "password": "password123"})
    return resp.json()["access_token"]
