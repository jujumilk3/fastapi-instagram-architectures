from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.post.schemas import PostCreate, PostResponse
from modular_monolith.modules.post.service import PostService
from modular_monolith.shared.database import get_db
from modular_monolith.shared.security import get_current_user_id

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(data: PostCreate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await PostService(db).create(user_id, data)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await PostService(db).get(post_id)


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await PostService(db).delete(post_id, user_id)
