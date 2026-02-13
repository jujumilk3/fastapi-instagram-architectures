from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered.database import get_db
from layered.schemas.story import StoryCreate, StoryResponse
from layered.security import get_current_user_id
from layered.services.story import StoryService

router = APIRouter(prefix="/api/stories", tags=["stories"])


@router.post("", response_model=StoryResponse, status_code=201)
async def create_story(
    data: StoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await StoryService(db).create(user_id, data)


@router.get("", response_model=list[StoryResponse])
async def get_my_stories(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await StoryService(db).get_my_stories(user_id)


@router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await StoryService(db).get_feed(user_id)


@router.delete("/{story_id}", status_code=204)
async def delete_story(
    story_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await StoryService(db).delete(story_id, user_id)
