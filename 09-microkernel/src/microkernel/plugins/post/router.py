from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from microkernel.core.database import get_db
from microkernel.core.security import get_current_user_id
from microkernel.plugins.post.schemas import CommentCreate, CommentResponse, PostCreate, PostResponse
from microkernel.plugins.post.service import CommentService, LikeService, PostService

router = APIRouter(tags=["posts"])


@router.post("/api/posts", response_model=PostResponse, status_code=201)
async def create_post(data: PostCreate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await PostService(db).create(user_id, data)


@router.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await PostService(db).get(post_id)


@router.delete("/api/posts/{post_id}", status_code=204)
async def delete_post(post_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await PostService(db).delete(post_id, user_id)


@router.post("/api/posts/{post_id}/likes")
async def toggle_like(post_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await LikeService(db).toggle(post_id, user_id)


@router.get("/api/posts/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(post_id: int, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await CommentService(db).get_by_post(post_id, limit, offset)


@router.post("/api/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(post_id: int, data: CommentCreate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await CommentService(db).create(post_id, user_id, data)


@router.delete("/api/posts/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await CommentService(db).delete(comment_id, user_id)
