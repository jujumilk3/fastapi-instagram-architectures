from fastapi import HTTPException, status

from clean.entities.social import Message
from clean.use_cases.interfaces.repositories import MessageRepository, UserRepository


class SendMessageUseCase:
    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def execute(self, sender_id: int, receiver_id: int, content: str) -> Message:
        if not await self.user_repo.get_by_id(receiver_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")
        return await self.message_repo.create(Message(sender_id=sender_id, receiver_id=receiver_id, content=content))
