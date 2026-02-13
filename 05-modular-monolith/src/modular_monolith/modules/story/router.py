from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modular_monolith.modules.story.schemas import StoryCreate, StoryResponse
from modular_monolith.modules.story.service import StoryService
from modular_monolith.shared.database import get_db
from modular_monolith.shared.security import get_current_user_id

router = APIRouter(prefix="/api/stories", tags=["stories"])


@router.post("", response_model=StoryResponse, status_code=201)
async def create_story(data: StoryCreate, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await StoryService(db).create(user_id, data)


@router.get("", response_model=list[StoryResponse])
async def get_my_stories(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await StoryService(db).get_my_stories(user_id)


@router.get("/feed", response_model=list[StoryResponse])
async def get_story_feed(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await StoryService(db).get_feed(user_id)


@router.delete("/{story_id}", status_code=204)
async def delete_story(story_id: int, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    await StoryService(db).delete(story_id, user_id)
