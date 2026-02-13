from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.user.router import router


class UserPlugin(Plugin):
    @property
    def name(self) -> str:
        return "user"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
