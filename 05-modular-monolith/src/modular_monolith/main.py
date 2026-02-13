from contextlib import asynccontextmanager

from fastapi import FastAPI

from modular_monolith.modules.auth import router as auth_router
from modular_monolith.modules.comment import router as comment_router
from modular_monolith.modules.feed import router as feed_router
from modular_monolith.modules.follow import router as follow_router
from modular_monolith.modules.like import router as like_router
from modular_monolith.modules.messaging import router as messaging_router
from modular_monolith.modules.notification import router as notification_router
from modular_monolith.modules.post import router as post_router
from modular_monolith.modules.search import router as search_router
from modular_monolith.modules.story import router as story_router
from modular_monolith.modules.user import router as user_router
from modular_monolith.shared.base_model import Base
from modular_monolith.shared.database import engine

# Import all models so Base.metadata knows about them
import modular_monolith.modules.auth.models  # noqa: F401
import modular_monolith.modules.post.models  # noqa: F401
import modular_monolith.modules.comment.models  # noqa: F401
import modular_monolith.modules.like.models  # noqa: F401
import modular_monolith.modules.follow.models  # noqa: F401
import modular_monolith.modules.story.models  # noqa: F401
import modular_monolith.modules.messaging.models  # noqa: F401
import modular_monolith.modules.notification.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Instagram Clone - Modular Monolith", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(like_router)
app.include_router(follow_router)
app.include_router(feed_router)
app.include_router(story_router)
app.include_router(messaging_router)
app.include_router(notification_router)
app.include_router(search_router)
