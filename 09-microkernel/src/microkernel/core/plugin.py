from abc import ABC, abstractmethod

from fastapi import FastAPI


class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def register(self, app: FastAPI) -> None: ...
