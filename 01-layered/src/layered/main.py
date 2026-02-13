from contextlib import asynccontextmanager

from fastapi import FastAPI

from layered.api import auth, feed, follow, message, notification, post, search, story, user
from layered.database import engine
from layered.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Instagram Clone - Layered Architecture", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(follow.router)
app.include_router(feed.router)
app.include_router(story.router)
app.include_router(message.router)
app.include_router(notification.router)
app.include_router(search.router)
