from clean.use_cases.interfaces.repositories import MessageRepository


class MarkMessagesReadUseCase:
    def __init__(self, message_repo: MessageRepository):
        self.message_repo = message_repo

    async def execute(self, user_id: int, sender_id: int) -> dict:
        await self.message_repo.mark_as_read(user_id, sender_id)
        return {"status": "ok"}
