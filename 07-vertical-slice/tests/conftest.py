import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from vertical_slice.models.base import Base
from vertical_slice.models.tables import (  # noqa: F401
    Comment,
    Follow,
    Hashtag,
    Like,
    Message,
    Notification,
    Post,
    PostHashtag,
    Story,
    User,
)
from vertical_slice.shared.database import get_db
from vertical_slice.main import app

TEST_DB_URL = "sqlite+aiosqlite:///./test_vertical_slice.db"
engine = create_async_engine(TEST_DB_URL, echo=False)
test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def override_get_db() -> AsyncGenerator[AsyncSession]:
    async with test_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db

BASE_URL = "http://testserver"


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture
async def second_user_token(client: AsyncClient) -> str:
    await client.post("/api/auth/register", json={
        "username": "seconduser",
        "email": "second@example.com",
        "password": "testpass123",
        "full_name": "Second User",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "second@example.com",
        "password": "testpass123",
    })
    return resp.json()["access_token"]
