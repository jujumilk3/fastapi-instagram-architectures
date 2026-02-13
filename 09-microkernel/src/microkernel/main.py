from contextlib import asynccontextmanager

from fastapi import FastAPI

from microkernel.core.base_model import Base
from microkernel.core.database import engine
from microkernel.core.registry import PluginRegistry
from microkernel.plugins import PLUGIN_LIST

# Import all models so Base.metadata knows about them
import microkernel.plugins.auth.models  # noqa: F401
import microkernel.plugins.post.models  # noqa: F401
import microkernel.plugins.follow.models  # noqa: F401
import microkernel.plugins.story.models  # noqa: F401
import microkernel.plugins.message.models  # noqa: F401
import microkernel.plugins.notification.models  # noqa: F401

registry = PluginRegistry()
for plugin in PLUGIN_LIST:
    registry.register(plugin)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Instagram Clone - Microkernel", lifespan=lifespan)

registry.startup(app)
