from contextlib import asynccontextmanager

from fastapi import FastAPI

from clean.frameworks.database import engine
from clean.frameworks.models import Base
from clean.interface_adapters.controllers.routers import (
    auth_router, feed_router, follow_router, message_router,
    notification_router, post_router, search_router, story_router, user_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Instagram Clone - Clean Architecture", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(follow_router)
app.include_router(feed_router)
app.include_router(story_router)
app.include_router(message_router)
app.include_router(notification_router)
app.include_router(search_router)
