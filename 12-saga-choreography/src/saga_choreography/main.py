from contextlib import asynccontextmanager

from fastapi import FastAPI

from saga_choreography.api.routers import (
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
from saga_choreography.choreography.handlers import (
    on_comment_added,
    on_post_created,
    on_post_liked,
    on_user_followed,
)
from saga_choreography.events.definitions import (
    COMMENT_ADDED,
    POST_CREATED,
    POST_LIKED,
    USER_FOLLOWED,
)
from saga_choreography.models.tables import *  # noqa: F401,F403
from saga_choreography.shared.database import Base, engine
from saga_choreography.shared.event_bus import event_bus


def _register_choreography_handlers() -> None:
    event_bus.clear()
    event_bus.subscribe(POST_CREATED, on_post_created)
    event_bus.subscribe(POST_LIKED, on_post_liked)
    event_bus.subscribe(COMMENT_ADDED, on_comment_added)
    event_bus.subscribe(USER_FOLLOWED, on_user_followed)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _register_choreography_handlers()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Instagram Clone - Saga Choreography Architecture",
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
