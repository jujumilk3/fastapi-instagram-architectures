from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.post.router import router


class PostPlugin(Plugin):
    @property
    def name(self) -> str:
        return "post"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
