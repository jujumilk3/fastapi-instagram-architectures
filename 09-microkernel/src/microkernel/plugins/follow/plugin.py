from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.follow.router import router


class FollowPlugin(Plugin):
    @property
    def name(self) -> str:
        return "follow"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
