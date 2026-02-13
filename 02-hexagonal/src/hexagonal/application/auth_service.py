import re

from fastapi import HTTPException, status

from hexagonal.domain.entities.post import Comment, Like, Post
from hexagonal.domain.entities.social import Follow, Hashtag, Message, Notification, Story
from hexagonal.domain.entities.user import User
from hexagonal.ports.outbound.repositories import (
    CommentRepositoryPort,
    FollowRepositoryPort,
    HashtagRepositoryPort,
    LikeRepositoryPort,
    MessageRepositoryPort,
    NotificationRepositoryPort,
    PostRepositoryPort,
    StoryRepositoryPort,
    UserRepositoryPort,
)
from hexagonal.ports.outbound.security import SecurityPort


class AuthService:
    def __init__(self, user_repo: UserRepositoryPort, security: SecurityPort):
        self.user_repo = user_repo
        self.security = security

    async def register(self, username: str, email: str, password: str, full_name: str | None = None) -> User:
        if await self.user_repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        if await self.user_repo.get_by_username(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        user = User(username=username, email=email, hashed_password=self.security.hash_password(password), full_name=full_name)
        return await self.user_repo.create(user)

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user or not self.security.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return self.security.create_token({"sub": str(user.id)})

    async def get_me(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user


class UserService:
    def __init__(self, user_repo: UserRepositoryPort, follow_repo: FollowRepositoryPort, post_repo: PostRepositoryPort):
        self.user_repo = user_repo
        self.follow_repo = follow_repo
        self.post_repo = post_repo

    async def get_profile(self, user_id: int) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {
            "id": user.id, "username": user.username, "full_name": user.full_name,
            "bio": user.bio, "profile_image_url": user.profile_image_url,
            "post_count": await self.post_repo.count_by_author(user_id),
            "follower_count": await self.follow_repo.count_followers(user_id),
            "following_count": await self.follow_repo.count_following(user_id),
        }

    async def update_me(self, user_id: int, **kwargs) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        return await self.user_repo.update(user)

    async def get_followers(self, user_id: int) -> list[User]:
        ids = await self.follow_repo.get_followers(user_id)
        users = []
        for uid in ids:
            u = await self.user_repo.get_by_id(uid)
            if u:
                users.append(u)
        return users

    async def get_following(self, user_id: int) -> list[User]:
        ids = await self.follow_repo.get_following(user_id)
        users = []
        for uid in ids:
            u = await self.user_repo.get_by_id(uid)
            if u:
                users.append(u)
        return users


class PostService:
    def __init__(self, post_repo: PostRepositoryPort, user_repo: UserRepositoryPort,
                 like_repo: LikeRepositoryPort, comment_repo: CommentRepositoryPort,
                 hashtag_repo: HashtagRepositoryPort):
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo
        self.hashtag_repo = hashtag_repo

    async def _enrich(self, post: Post) -> dict:
        author = await self.user_repo.get_by_id(post.author_id)
        like_count = await self.like_repo.count_by_post(post.id)
        comments = await self.comment_repo.get_by_post(post.id, 0, 0)
        return {
            "id": post.id, "author_id": post.author_id,
            "author_username": author.username if author else None,
            "content": post.content, "image_url": post.image_url,
            "like_count": like_count, "comment_count": len(comments),
            "created_at": post.created_at,
        }

    async def create(self, author_id: int, content: str | None = None, image_url: str | None = None) -> dict:
        post = await self.post_repo.create(Post(author_id=author_id, content=content, image_url=image_url))
        if content:
            for tag in re.findall(r"#(\w+)", content):
                h = await self.hashtag_repo.get_or_create(tag.lower())
                await self.hashtag_repo.link_post(post.id, h.id)
        return await self._enrich(post)

    async def get(self, post_id: int) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return await self._enrich(post)

    async def get_by_author(self, author_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
        posts = await self.post_repo.get_by_author(author_id, limit, offset)
        return [await self._enrich(p) for p in posts]

    async def delete(self, post_id: int, user_id: int) -> None:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if post.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your post")
        await self.hashtag_repo.unlink_post(post_id)
        await self.post_repo.delete(post_id)


class CommentService:
    def __init__(self, comment_repo: CommentRepositoryPort, post_repo: PostRepositoryPort,
                 user_repo: UserRepositoryPort, notification_repo: NotificationRepositoryPort):
        self.comment_repo = comment_repo
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo

    async def create(self, post_id: int, author_id: int, content: str) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        comment = await self.comment_repo.create(Comment(post_id=post_id, author_id=author_id, content=content))
        if post.author_id != author_id:
            await self.notification_repo.create(Notification(
                user_id=post.author_id, actor_id=author_id, type="comment",
                reference_id=post_id, message="commented on your post",
            ))
        return {"id": comment.id, "post_id": comment.post_id, "author_id": comment.author_id,
                "content": comment.content, "created_at": comment.created_at}

    async def get_by_post(self, post_id: int, limit: int = 50, offset: int = 0) -> list[dict]:
        comments = await self.comment_repo.get_by_post(post_id, limit, offset)
        result = []
        for c in comments:
            author = await self.user_repo.get_by_id(c.author_id)
            result.append({
                "id": c.id, "post_id": c.post_id, "author_id": c.author_id,
                "author_username": author.username if author else None,
                "content": c.content, "created_at": c.created_at,
            })
        return result

    async def delete(self, comment_id: int, user_id: int) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
        await self.comment_repo.delete(comment_id)


class LikeService:
    def __init__(self, like_repo: LikeRepositoryPort, post_repo: PostRepositoryPort,
                 notification_repo: NotificationRepositoryPort):
        self.like_repo = like_repo
        self.post_repo = post_repo
        self.notification_repo = notification_repo

    async def toggle(self, post_id: int, user_id: int) -> dict:
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        existing = await self.like_repo.get(post_id, user_id)
        if existing:
            await self.like_repo.delete(post_id, user_id)
            liked = False
        else:
            await self.like_repo.create(Like(post_id=post_id, user_id=user_id))
            liked = True
            if post.author_id != user_id:
                await self.notification_repo.create(Notification(
                    user_id=post.author_id, actor_id=user_id, type="like",
                    reference_id=post_id, message="liked your post",
                ))
        count = await self.like_repo.count_by_post(post_id)
        return {"liked": liked, "like_count": count}


class FollowService:
    def __init__(self, follow_repo: FollowRepositoryPort, user_repo: UserRepositoryPort,
                 notification_repo: NotificationRepositoryPort):
        self.follow_repo = follow_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo

    async def follow(self, follower_id: int, following_id: int) -> dict:
        if follower_id == following_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")
        if not await self.user_repo.get_by_id(following_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if await self.follow_repo.get(follower_id, following_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following")
        await self.follow_repo.create(Follow(follower_id=follower_id, following_id=following_id))
        await self.notification_repo.create(Notification(
            user_id=following_id, actor_id=follower_id, type="follow", message="started following you",
        ))
        return {"following": True}

    async def unfollow(self, follower_id: int, following_id: int) -> dict:
        if not await self.follow_repo.get(follower_id, following_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not following")
        await self.follow_repo.delete(follower_id, following_id)
        return {"following": False}


class FeedService:
    def __init__(self, post_repo: PostRepositoryPort, follow_repo: FollowRepositoryPort,
                 user_repo: UserRepositoryPort, like_repo: LikeRepositoryPort,
                 comment_repo: CommentRepositoryPort):
        self.post_service = PostService(post_repo, user_repo, like_repo, comment_repo, None)
        self.post_repo = post_repo
        self.follow_repo = follow_repo

    async def get_feed(self, user_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
        following_ids = await self.follow_repo.get_following(user_id)
        following_ids.append(user_id)
        posts = await self.post_repo.get_feed(following_ids, limit, offset)
        return [await self.post_service._enrich(p) for p in posts]


class StoryService:
    def __init__(self, story_repo: StoryRepositoryPort, follow_repo: FollowRepositoryPort,
                 user_repo: UserRepositoryPort):
        self.story_repo = story_repo
        self.follow_repo = follow_repo
        self.user_repo = user_repo

    async def _enrich(self, story: Story) -> dict:
        author = await self.user_repo.get_by_id(story.author_id)
        return {
            "id": story.id, "author_id": story.author_id,
            "author_username": author.username if author else None,
            "image_url": story.image_url, "content": story.content,
            "created_at": story.created_at,
        }

    async def create(self, author_id: int, image_url: str | None, content: str | None) -> dict:
        story = await self.story_repo.create(Story(author_id=author_id, image_url=image_url, content=content))
        return {"id": story.id, "author_id": story.author_id, "image_url": story.image_url,
                "content": story.content, "created_at": story.created_at}

    async def get_my_stories(self, user_id: int) -> list[dict]:
        stories = await self.story_repo.get_active_by_author(user_id)
        return [await self._enrich(s) for s in stories]

    async def get_feed(self, user_id: int) -> list[dict]:
        ids = await self.follow_repo.get_following(user_id)
        ids.append(user_id)
        stories = await self.story_repo.get_feed(ids)
        return [await self._enrich(s) for s in stories]

    async def delete(self, story_id: int, user_id: int) -> None:
        story = await self.story_repo.get_by_id(story_id)
        if not story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
        if story.author_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your story")
        await self.story_repo.delete(story_id)


class MessageService:
    def __init__(self, message_repo: MessageRepositoryPort, user_repo: UserRepositoryPort):
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def send(self, sender_id: int, receiver_id: int, content: str) -> Message:
        if not await self.user_repo.get_by_id(receiver_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")
        return await self.message_repo.create(Message(sender_id=sender_id, receiver_id=receiver_id, content=content))

    async def get_conversations(self, user_id: int) -> list[dict]:
        return await self.message_repo.get_conversations(user_id)

    async def get_conversation(self, user_id: int, other_user_id: int, limit: int, offset: int) -> list[Message]:
        return await self.message_repo.get_conversation(user_id, other_user_id, limit, offset)

    async def mark_read(self, user_id: int, sender_id: int) -> dict:
        await self.message_repo.mark_as_read(user_id, sender_id)
        return {"status": "ok"}


class NotificationService:
    def __init__(self, notification_repo: NotificationRepositoryPort):
        self.notification_repo = notification_repo

    async def get_notifications(self, user_id: int, limit: int, offset: int) -> list[Notification]:
        return await self.notification_repo.get_by_user(user_id, limit, offset)

    async def mark_read(self, notification_id: int, user_id: int) -> dict:
        await self.notification_repo.mark_read(notification_id, user_id)
        return {"status": "ok"}

    async def mark_all_read(self, user_id: int) -> dict:
        await self.notification_repo.mark_all_read(user_id)
        return {"status": "ok"}


class SearchService:
    def __init__(self, user_repo: UserRepositoryPort, hashtag_repo: HashtagRepositoryPort,
                 like_repo: LikeRepositoryPort, comment_repo: CommentRepositoryPort):
        self.user_repo = user_repo
        self.hashtag_repo = hashtag_repo
        self.like_repo = like_repo
        self.comment_repo = comment_repo

    async def search_users(self, query: str, limit: int = 20) -> list[User]:
        return await self.user_repo.search(query, limit)

    async def search_hashtags(self, query: str, limit: int = 20) -> list[Hashtag]:
        return await self.hashtag_repo.search(query, limit)

    async def get_posts_by_hashtag(self, tag: str, limit: int = 20, offset: int = 0) -> list[dict]:
        posts = await self.hashtag_repo.get_posts_by_hashtag(tag, limit, offset)
        result = []
        for p in posts:
            author = await self.user_repo.get_by_id(p.author_id)
            like_count = await self.like_repo.count_by_post(p.id)
            comments = await self.comment_repo.get_by_post(p.id, 0, 0)
            result.append({
                "id": p.id, "author_id": p.author_id,
                "author_username": author.username if author else None,
                "content": p.content, "image_url": p.image_url,
                "like_count": like_count, "comment_count": len(comments),
                "created_at": p.created_at,
            })
        return result
