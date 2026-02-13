from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.story.router import router


class StoryPlugin(Plugin):
    @property
    def name(self) -> str:
        return "story"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
