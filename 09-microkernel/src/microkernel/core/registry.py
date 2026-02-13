from fastapi import FastAPI

from microkernel.core.plugin import Plugin


class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self._plugins[plugin.name] = plugin

    def get_all(self) -> list[Plugin]:
        return list(self._plugins.values())

    def startup(self, app: FastAPI) -> None:
        for plugin in self._plugins.values():
            plugin.register(app)
