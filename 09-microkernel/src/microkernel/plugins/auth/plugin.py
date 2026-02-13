from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.auth.router import router


class AuthPlugin(Plugin):
    @property
    def name(self) -> str:
        return "auth"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
