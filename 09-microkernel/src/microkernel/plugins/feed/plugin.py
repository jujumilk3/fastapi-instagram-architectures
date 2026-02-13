from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.feed.router import router


class FeedPlugin(Plugin):
    @property
    def name(self) -> str:
        return "feed"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
