from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.message.router import router


class MessagePlugin(Plugin):
    @property
    def name(self) -> str:
        return "message"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
