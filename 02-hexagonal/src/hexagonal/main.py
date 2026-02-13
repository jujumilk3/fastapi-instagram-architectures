from contextlib import asynccontextmanager

from fastapi import FastAPI

from hexagonal.adapters.inbound.api.dependencies import engine
from hexagonal.adapters.inbound.api.routers import (
    auth_router, feed_router, follow_router, message_router,
    notification_router, post_router, search_router, story_router, user_router,
)
from hexagonal.adapters.outbound.persistence.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Instagram Clone - Hexagonal Architecture", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(follow_router)
app.include_router(feed_router)
app.include_router(story_router)
app.include_router(message_router)
app.include_router(notification_router)
app.include_router(search_router)
