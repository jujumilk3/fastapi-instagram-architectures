from contextlib import asynccontextmanager

from fastapi import FastAPI

from actor_model.actors.comment_actor import CommentActor
from actor_model.actors.feed_actor import FeedActor
from actor_model.actors.follow_actor import FollowActor
from actor_model.actors.like_actor import LikeActor
from actor_model.actors.message_actor import MessageActor
from actor_model.actors.notification_actor import NotificationActor
from actor_model.actors.post_actor import PostActor
from actor_model.actors.registry import ActorRegistry
from actor_model.actors.search_actor import SearchActor
from actor_model.actors.story_actor import StoryActor
from actor_model.actors.user_actor import UserActor
from actor_model.api.routers import (
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
from actor_model.models.base import Base
from actor_model.shared.database import async_session, engine


def create_registry(db_factory=None) -> ActorRegistry:
    if db_factory is None:
        db_factory = async_session

    registry = ActorRegistry()
    registry._db_factory = db_factory

    registry.register("user", UserActor())
    registry.register("post", PostActor())
    registry.register("comment", CommentActor(registry))
    registry.register("like", LikeActor(registry))
    registry.register("follow", FollowActor(registry))
    registry.register("feed", FeedActor())
    registry.register("story", StoryActor())
    registry.register("message", MessageActor())
    registry.register("notification", NotificationActor())
    registry.register("search", SearchActor())

    return registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    registry = create_registry()
    await registry.start_all()
    app.state.registry = registry

    yield

    await registry.stop_all()
    await engine.dispose()


app = FastAPI(
    title="Instagram Clone - Actor Model",
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
