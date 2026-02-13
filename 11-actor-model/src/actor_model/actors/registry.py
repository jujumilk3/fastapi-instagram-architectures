from actor_model.actors.base import Actor, Message


class ActorRegistry:
    def __init__(self):
        self._actors: dict[str, Actor] = {}

    def register(self, name: str, actor: Actor):
        self._actors[name] = actor

    def get(self, name: str) -> Actor:
        return self._actors[name]

    async def send(self, name: str, message: Message):
        actor = self._actors[name]
        await actor.send(message)

    async def start_all(self):
        for actor in self._actors.values():
            await actor.start()

    async def stop_all(self):
        for actor in self._actors.values():
            await actor.stop()
