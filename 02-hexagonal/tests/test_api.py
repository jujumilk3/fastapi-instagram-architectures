import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAuth:
    async def test_register(self, auth_client: AsyncClient):
        assert auth_client.headers.get("Authorization") is not None

    async def test_register_duplicate_email(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/auth/register", json={
            "username": "another",
            "email": "test@example.com",
            "password": "pass123",
        })
        assert resp.status_code == 400
        assert "Email already registered" in resp.json()["detail"]

    async def test_login(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_invalid_credentials(self, client: AsyncClient):
        resp = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    async def test_me(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    async def test_me_unauthorized(self, client: AsyncClient):
        saved = client.headers.pop("Authorization", None)
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401
        if saved:
            client.headers["Authorization"] = saved


class TestUser:
    async def test_get_profile(self, auth_client: AsyncClient):
        me = await auth_client.get("/api/auth/me")
        user_id = me.json()["id"]
        resp = await auth_client.get(f"/api/users/{user_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert "post_count" in data
        assert "follower_count" in data

    async def test_update_me(self, auth_client: AsyncClient):
        resp = await auth_client.put("/api/users/me", json={
            "bio": "Hello world",
            "full_name": "Updated Name",
        })
        assert resp.status_code == 200
        assert resp.json()["bio"] == "Hello world"
        assert resp.json()["full_name"] == "Updated Name"

    async def test_get_nonexistent_user(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/users/99999")
        assert resp.status_code == 404


class TestPost:
    async def test_create_post(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/posts", json={
            "content": "My first post! #hello #world",
            "image_url": "https://example.com/img.jpg",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "My first post! #hello #world"
        assert data["image_url"] == "https://example.com/img.jpg"
        assert data["author_username"] == "testuser"

    async def test_get_post(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/posts", json={
            "content": "Get me post",
        })
        post_id = create_resp.json()["id"]
        resp = await auth_client.get(f"/api/posts/{post_id}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "Get me post"

    async def test_get_user_posts(self, auth_client: AsyncClient):
        me = await auth_client.get("/api/auth/me")
        user_id = me.json()["id"]
        resp = await auth_client.get(f"/api/users/{user_id}/posts")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    async def test_delete_post(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/posts", json={
            "content": "To be deleted",
        })
        post_id = create_resp.json()["id"]
        resp = await auth_client.delete(f"/api/posts/{post_id}")
        assert resp.status_code == 204

        get_resp = await auth_client.get(f"/api/posts/{post_id}")
        assert get_resp.status_code == 404


class TestComment:
    async def test_create_and_get_comments(self, auth_client: AsyncClient):
        post_resp = await auth_client.post("/api/posts", json={
            "content": "Post for comments",
        })
        post_id = post_resp.json()["id"]

        comment_resp = await auth_client.post(f"/api/posts/{post_id}/comments", json={
            "content": "Nice post!",
        })
        assert comment_resp.status_code == 201
        assert comment_resp.json()["content"] == "Nice post!"

        list_resp = await auth_client.get(f"/api/posts/{post_id}/comments")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

    async def test_delete_comment(self, auth_client: AsyncClient):
        post_resp = await auth_client.post("/api/posts", json={
            "content": "Post for comment deletion",
        })
        post_id = post_resp.json()["id"]

        comment_resp = await auth_client.post(f"/api/posts/{post_id}/comments", json={
            "content": "To be deleted",
        })
        comment_id = comment_resp.json()["id"]

        resp = await auth_client.delete(f"/api/posts/comments/{comment_id}")
        assert resp.status_code == 204


class TestLike:
    async def test_toggle_like(self, auth_client: AsyncClient):
        post_resp = await auth_client.post("/api/posts", json={
            "content": "Post for likes",
        })
        post_id = post_resp.json()["id"]

        like_resp = await auth_client.post(f"/api/posts/{post_id}/likes")
        assert like_resp.status_code == 200
        assert like_resp.json()["liked"] is True
        assert like_resp.json()["like_count"] == 1

        unlike_resp = await auth_client.post(f"/api/posts/{post_id}/likes")
        assert unlike_resp.status_code == 200
        assert unlike_resp.json()["liked"] is False
        assert unlike_resp.json()["like_count"] == 0


class TestFollow:
    async def test_follow_and_unfollow(self, auth_client: AsyncClient, second_user_token: str):
        saved = auth_client.headers.get("Authorization")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        me_resp = await auth_client.get("/api/auth/me")
        second_user_id = me_resp.json()["id"]
        auth_client.headers["Authorization"] = saved

        resp = await auth_client.post(f"/api/follow/{second_user_id}")
        assert resp.status_code == 200
        assert resp.json()["following"] is True

        unfollow_resp = await auth_client.delete(f"/api/follow/{second_user_id}")
        assert unfollow_resp.status_code == 200
        assert unfollow_resp.json()["following"] is False

    async def test_cannot_follow_self(self, auth_client: AsyncClient):
        me_resp = await auth_client.get("/api/auth/me")
        my_id = me_resp.json()["id"]
        resp = await auth_client.post(f"/api/follow/{my_id}")
        assert resp.status_code == 400
        assert "Cannot follow yourself" in resp.json()["detail"]

    async def test_followers_and_following_lists(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        saved = auth_client.headers.get("Authorization")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        me_resp = await auth_client.get("/api/auth/me")
        second_user_id = me_resp.json()["id"]
        auth_client.headers["Authorization"] = saved

        await auth_client.post(f"/api/follow/{second_user_id}")

        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]

        followers_resp = await auth_client.get(f"/api/users/{second_user_id}/followers")
        assert followers_resp.status_code == 200

        following_resp = await auth_client.get(f"/api/users/{my_id}/following")
        assert following_resp.status_code == 200

        await auth_client.delete(f"/api/follow/{second_user_id}")


class TestFeed:
    async def test_get_feed(self, auth_client: AsyncClient, second_user_token: str):
        saved = auth_client.headers.get("Authorization")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        me_resp = await auth_client.get("/api/auth/me")
        second_user_id = me_resp.json()["id"]

        await auth_client.post("/api/posts", json={
            "content": "Second user post for feed",
        })
        auth_client.headers["Authorization"] = saved

        await auth_client.post(f"/api/follow/{second_user_id}")

        resp = await auth_client.get("/api/feed")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

        await auth_client.delete(f"/api/follow/{second_user_id}")


class TestStory:
    async def test_create_and_get_stories(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/stories", json={
            "image_url": "https://example.com/story.jpg",
            "content": "My story",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["image_url"] == "https://example.com/story.jpg"

        list_resp = await auth_client.get("/api/stories")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

    async def test_story_feed(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/stories/feed")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_delete_story(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/stories", json={
            "content": "Story to delete",
        })
        story_id = create_resp.json()["id"]

        resp = await auth_client.delete(f"/api/stories/{story_id}")
        assert resp.status_code == 204


class TestMessage:
    async def test_send_and_get_messages(self, auth_client: AsyncClient, second_user_token: str):
        saved = auth_client.headers.get("Authorization")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        me_resp = await auth_client.get("/api/auth/me")
        second_user_id = me_resp.json()["id"]
        auth_client.headers["Authorization"] = saved

        resp = await auth_client.post("/api/messages", json={
            "receiver_id": second_user_id,
            "content": "Hello there!",
        })
        assert resp.status_code == 201
        assert resp.json()["content"] == "Hello there!"

        conv_resp = await auth_client.get(f"/api/messages/{second_user_id}")
        assert conv_resp.status_code == 200
        assert len(conv_resp.json()) >= 1

    async def test_mark_read(self, auth_client: AsyncClient, second_user_token: str):
        saved = auth_client.headers.get("Authorization")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        me_resp = await auth_client.get("/api/auth/me")
        second_user_id = me_resp.json()["id"]

        # Get primary user id
        auth_client.headers["Authorization"] = saved
        primary_me = await auth_client.get("/api/auth/me")
        primary_user_id = primary_me.json()["id"]

        # Send message from second user to primary user
        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        await auth_client.post("/api/messages", json={
            "receiver_id": primary_user_id,
            "content": "Read this!",
        })

        # Mark as read by primary user
        auth_client.headers["Authorization"] = saved
        resp = await auth_client.post(f"/api/messages/{second_user_id}/read")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_list_conversations(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/messages")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestNotification:
    async def test_list_notifications(self, auth_client: AsyncClient, second_user_token: str):
        saved = auth_client.headers.get("Authorization")

        # Follow from second user to trigger a notification for primary user
        me_resp = await auth_client.get("/api/auth/me")
        primary_user_id = me_resp.json()["id"]

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        await auth_client.post(f"/api/follow/{primary_user_id}")

        # Check notifications for primary user
        auth_client.headers["Authorization"] = saved
        resp = await auth_client.get("/api/notifications")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

        # Cleanup: unfollow
        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        await auth_client.delete(f"/api/follow/{primary_user_id}")
        auth_client.headers["Authorization"] = saved

    async def test_mark_all_read(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/notifications/read-all")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_notification_created_on_follow(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        saved = auth_client.headers.get("Authorization")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        me_resp = await auth_client.get("/api/auth/me")
        second_user_id = me_resp.json()["id"]
        auth_client.headers["Authorization"] = saved

        me = await auth_client.get("/api/auth/me")
        primary_user_id = me.json()["id"]

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        await auth_client.post(f"/api/follow/{primary_user_id}")

        auth_client.headers["Authorization"] = saved
        notif_resp = await auth_client.get("/api/notifications")
        assert notif_resp.status_code == 200
        notifications = notif_resp.json()
        follow_notifs = [n for n in notifications if n["type"] == "follow"]
        assert len(follow_notifs) >= 1

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        await auth_client.delete(f"/api/follow/{primary_user_id}")
        auth_client.headers["Authorization"] = saved

    async def test_notification_created_on_like(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        saved = auth_client.headers.get("Authorization")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        post_resp = await auth_client.post(
            "/api/posts",
            json={"content": "Like for notif", "image_url": None},
        )
        post_id = post_resp.json()["id"]
        auth_client.headers["Authorization"] = saved

        await auth_client.post(f"/api/posts/{post_id}/likes")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        notif_resp = await auth_client.get("/api/notifications")
        assert notif_resp.status_code == 200
        notifications = notif_resp.json()
        like_notifs = [n for n in notifications if n["type"] == "like"]
        assert len(like_notifs) >= 1
        auth_client.headers["Authorization"] = saved

    async def test_mark_single_notification_read(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        saved = auth_client.headers.get("Authorization")

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        notif_resp = await auth_client.get("/api/notifications")
        notifications = notif_resp.json()
        if notifications:
            notif_id = notifications[0]["id"]
            mark_resp = await auth_client.post(
                f"/api/notifications/{notif_id}/read",
            )
            assert mark_resp.status_code == 200
        auth_client.headers["Authorization"] = saved


class TestSearch:
    async def test_search_users(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/search/users", params={"q": "test"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1
        assert resp.json()[0]["username"] == "testuser"

    async def test_search_hashtags(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/search/hashtags", params={"q": "hello"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    async def test_get_posts_by_hashtag(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/search/posts/hashtag/hello")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1
