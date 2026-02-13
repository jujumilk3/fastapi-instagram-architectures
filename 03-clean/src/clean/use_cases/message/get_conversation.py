from clean.entities.social import Message
from clean.use_cases.interfaces.repositories import MessageRepository


class GetConversationUseCase:
    def __init__(self, message_repo: MessageRepository):
        self.message_repo = message_repo

    async def execute(self, user_id: int, other_user_id: int, limit: int, offset: int) -> list[Message]:
        return await self.message_repo.get_conversation(user_id, other_user_id, limit, offset)
