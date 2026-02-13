from contextlib import asynccontextmanager

from fastapi import FastAPI

from event_driven.api.routers import (
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
from event_driven.consumers.hashtag_consumer import on_post_created
from event_driven.consumers.notification_consumer import (
    on_comment_added,
    on_post_liked,
    on_user_followed,
)
from event_driven.events.definitions import COMMENT_ADDED, POST_CREATED, POST_LIKED, USER_FOLLOWED
from event_driven.models.tables import *  # noqa: F401,F403
from event_driven.shared.database import Base, engine
from event_driven.shared.event_broker import broker


def _register_consumers() -> None:
    broker.clear()
    broker.subscribe(POST_LIKED, on_post_liked)
    broker.subscribe(COMMENT_ADDED, on_comment_added)
    broker.subscribe(USER_FOLLOWED, on_user_followed)
    broker.subscribe(POST_CREATED, on_post_created)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _register_consumers()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Instagram Clone - Event-Driven Architecture",
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
