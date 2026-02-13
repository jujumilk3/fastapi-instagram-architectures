from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.comment.schemas import CommentCreate, CommentResponse
from modular_monolith.modules.comment.service import CommentService
from modular_monolith.shared.database import get_db
from modular_monolith.shared.security import get_current_user_id

router = APIRouter(tags=["comments"])


@router.get("/api/posts/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(post_id: int, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await CommentService(db).get_by_post(post_id, limit, offset)


@router.post("/api/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(post_id: int, data: CommentCreate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await CommentService(db).create(post_id, user_id, data)


@router.delete("/api/posts/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await CommentService(db).delete(comment_id, user_id)
