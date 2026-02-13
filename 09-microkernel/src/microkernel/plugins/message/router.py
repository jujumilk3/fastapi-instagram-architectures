from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.core.database import get_db
from microkernel.core.security import get_current_user_id
from microkernel.plugins.message.schemas import ConversationResponse, MessageCreate, MessageResponse
from microkernel.plugins.message.service import MessageService

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("", response_model=MessageResponse, status_code=201)
async def send_message(data: MessageCreate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await MessageService(db).send(user_id, data)


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await MessageService(db).get_conversations(user_id)


@router.get("/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation(other_user_id: int, limit: int = 50, offset: int = 0, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await MessageService(db).get_conversation(user_id, other_user_id, limit, offset)


@router.post("/{sender_id}/read")
async def mark_read(sender_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await MessageService(db).mark_read(user_id, sender_id)
