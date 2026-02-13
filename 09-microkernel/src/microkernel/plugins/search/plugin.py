from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.search.router import router


class SearchPlugin(Plugin):
    @property
    def name(self) -> str:
        return "search"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
