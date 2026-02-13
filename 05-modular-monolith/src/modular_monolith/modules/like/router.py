from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.like.service import LikeService
from modular_monolith.shared.database import get_db
from modular_monolith.shared.security import get_current_user_id

router = APIRouter(tags=["likes"])


@router.post("/api/posts/{post_id}/likes")
async def toggle_like(post_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await LikeService(db).toggle(post_id, user_id)
