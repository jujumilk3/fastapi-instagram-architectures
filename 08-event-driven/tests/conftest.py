import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from event_driven.shared.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_event_driven.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession]:
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    from event_driven.models.tables import (  # noqa: F401
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
    from event_driven.main import _register_consumers

    _register_consumers()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    from event_driven.main import app

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    await client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
        },
    )
    login_resp = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = login_resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def second_user_token(client: AsyncClient) -> str:
    await client.post(
        "/api/auth/register",
        json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
            "full_name": "Other User",
        },
    )
    login_resp = await client.post(
        "/api/auth/login",
        json={"email": "other@example.com", "password": "password123"},
    )
    return login_resp.json()["access_token"]
