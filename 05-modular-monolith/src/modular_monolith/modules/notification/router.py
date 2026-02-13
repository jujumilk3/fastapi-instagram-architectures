from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.notification.schemas import NotificationResponse
from modular_monolith.modules.notification.service import NotificationService
from modular_monolith.shared.database import get_db
from modular_monolith.shared.security import get_current_user_id

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(limit: int = 50, offset: int = 0, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await NotificationService(db).get_notifications(user_id, limit, offset)


@router.post("/{notification_id}/read")
async def mark_read(notification_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await NotificationService(db).mark_read(notification_id, user_id)


@router.post("/read-all")
async def mark_all_read(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await NotificationService(db).mark_all_read(user_id)
