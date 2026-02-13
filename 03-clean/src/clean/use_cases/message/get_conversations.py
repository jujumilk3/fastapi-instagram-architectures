from clean.use_cases.interfaces.repositories import MessageRepository


class GetConversationsUseCase:
    def __init__(self, message_repo: MessageRepository):
        self.message_repo = message_repo

    async def execute(self, user_id: int) -> list[dict]:
        return await self.message_repo.get_conversations(user_id)
