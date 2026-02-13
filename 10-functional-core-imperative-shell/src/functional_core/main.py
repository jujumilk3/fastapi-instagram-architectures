from contextlib import asynccontextmanager

from fastapi import FastAPI

from functional_core.api.routers import (
    auth_router,
    feed_router,
    follow_router,
    message_router,
    notification_router,
    post_router,
    search_router,
    story_router,
    user_router,
)
from functional_core.shell.database import engine
from functional_core.shell.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Instagram Clone - Functional Core, Imperative Shell",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(follow_router)
app.include_router(feed_router)
app.include_router(story_router)
app.include_router(message_router)
app.include_router(notification_router)
app.include_router(search_router)
