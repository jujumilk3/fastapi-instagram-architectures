from fastapi import FastAPI

from microkernel.core.plugin import Plugin
from microkernel.plugins.notification.router import router


class NotificationPlugin(Plugin):
    @property
    def name(self) -> str:
        return "notification"

    def register(self, app: FastAPI) -> None:
        app.include_router(router)
