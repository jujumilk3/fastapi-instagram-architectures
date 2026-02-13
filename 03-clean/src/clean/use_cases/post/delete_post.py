from fastapi import HTTPException, status

from clean.use_cases.interfaces.repositories import HashtagRepository, PostRepository


class DeletePostUseCase:
    def __init__(self, post_repo: PostRepository, hashtag_repo: HashtagRepository):
        self.post_repo = post_repo
        self.hashtag_repo = hashtag_repo

    async def execute(self, post_id: int, user_id: int) -> None:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if post.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
        await self.hashtag_repo.unlink_post(post_id)
        await self.post_repo.delete(post_id)
