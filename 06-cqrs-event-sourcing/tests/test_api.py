import pytest
from httpx import AsyncClient


class TestAuth:
    async def test_register(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={
                "username": "authuser",
                "email": "auth@example.com",
                "password": "password123",
                "full_name": "Auth User",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "authuser"
        assert data["email"] == "auth@example.com"
        assert data["full_name"] == "Auth User"

    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post(
            "/api/auth/register",
            json={
                "username": "dupuser1",
                "email": "dup@example.com",
                "password": "password123",
            },
        )
        resp = await client.post(
            "/api/auth/register",
            json={
                "username": "dupuser2",
                "email": "dup@example.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    async def test_login(self, client: AsyncClient):
        await client.post(
            "/api/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "password123",
            },
        )
        resp = await client.post(
            "/api/auth/login",
            json={"email": "login@example.com", "password": "password123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_invalid_credentials(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    async def test_me(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    async def test_me_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401


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
        resp = await auth_client.put(
            "/api/users/me",
            json={"bio": "Hello world", "full_name": "Updated Name"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["bio"] == "Hello world"
        assert data["full_name"] == "Updated Name"

    async def test_nonexistent_user(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/users/99999")
        assert resp.status_code == 404


class TestPost:
    async def test_create_post(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/api/posts",
            json={"content": "Hello #world!", "image_url": "https://img.test/1.jpg"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "Hello #world!"
        assert data["image_url"] == "https://img.test/1.jpg"
        assert data["like_count"] == 0

    async def test_get_post(self, auth_client: AsyncClient):
        create = await auth_client.post(
            "/api/posts",
            json={"content": "Get me", "image_url": None},
        )
        post_id = create.json()["id"]
        resp = await auth_client.get(f"/api/posts/{post_id}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "Get me"

    async def test_delete_post(self, auth_client: AsyncClient):
        create = await auth_client.post(
            "/api/posts",
            json={"content": "To delete", "image_url": None},
        )
        post_id = create.json()["id"]
        resp = await auth_client.delete(f"/api/posts/{post_id}")
        assert resp.status_code == 204

        get_resp = await auth_client.get(f"/api/posts/{post_id}")
        assert get_resp.status_code == 404

    async def test_get_user_posts(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/posts",
            json={"content": "User post", "image_url": None},
        )
        me = await auth_client.get("/api/auth/me")
        user_id = me.json()["id"]
        resp = await auth_client.get(f"/api/users/{user_id}/posts")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1


class TestComment:
    async def test_create_and_get_comments(self, auth_client: AsyncClient):
        post = await auth_client.post(
            "/api/posts",
            json={"content": "Comment target", "image_url": None},
        )
        post_id = post.json()["id"]

        comment_resp = await auth_client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "Nice post!"},
        )
        assert comment_resp.status_code == 201
        assert comment_resp.json()["content"] == "Nice post!"

        comments = await auth_client.get(f"/api/posts/{post_id}/comments")
        assert comments.status_code == 200
        assert len(comments.json()) >= 1

    async def test_delete_comment(self, auth_client: AsyncClient):
        post = await auth_client.post(
            "/api/posts",
            json={"content": "For comment delete", "image_url": None},
        )
        post_id = post.json()["id"]
        comment = await auth_client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "To remove"},
        )
        comment_id = comment.json()["id"]

        resp = await auth_client.delete(f"/api/posts/comments/{comment_id}")
        assert resp.status_code == 204


class TestLike:
    async def test_toggle_like(self, auth_client: AsyncClient):
        post = await auth_client.post(
            "/api/posts",
            json={"content": "Like me", "image_url": None},
        )
        post_id = post.json()["id"]

        like_resp = await auth_client.post(f"/api/posts/{post_id}/likes")
        assert like_resp.status_code == 200
        assert like_resp.json()["liked"] is True
        assert like_resp.json()["like_count"] == 1

        unlike_resp = await auth_client.post(f"/api/posts/{post_id}/likes")
        assert unlike_resp.status_code == 200
        assert unlike_resp.json()["liked"] is False
        assert unlike_resp.json()["like_count"] == 0


class TestFollow:
    async def test_follow_and_unfollow(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        other_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        other_id = other_me.json()["id"]

        follow_resp = await auth_client.post(f"/api/follow/{other_id}")
        assert follow_resp.status_code == 200
        assert follow_resp.json()["following"] is True

        unfollow_resp = await auth_client.delete(f"/api/follow/{other_id}")
        assert unfollow_resp.status_code == 200
        assert unfollow_resp.json()["following"] is False

    async def test_cannot_follow_self(self, auth_client: AsyncClient):
        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]
        resp = await auth_client.post(f"/api/follow/{my_id}")
        assert resp.status_code == 400
        assert "yourself" in resp.json()["detail"].lower()


class TestFeed:
    async def test_get_feed(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/posts",
            json={"content": "Feed post", "image_url": None},
        )
        resp = await auth_client.get("/api/feed")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestStory:
    async def test_create_and_get_stories(self, auth_client: AsyncClient):
        create_resp = await auth_client.post(
            "/api/stories",
            json={"image_url": "https://img.test/story.jpg", "content": "My story"},
        )
        assert create_resp.status_code == 201
        data = create_resp.json()
        assert data["content"] == "My story"

        stories_resp = await auth_client.get("/api/stories")
        assert stories_resp.status_code == 200
        assert len(stories_resp.json()) >= 1

    async def test_story_feed(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/stories/feed")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_delete_story(self, auth_client: AsyncClient):
        create = await auth_client.post(
            "/api/stories",
            json={"image_url": "https://img.test/del.jpg", "content": "Delete me"},
        )
        story_id = create.json()["id"]
        resp = await auth_client.delete(f"/api/stories/{story_id}")
        assert resp.status_code == 204


class TestMessage:
    async def test_send_and_get_messages(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        other_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        other_id = other_me.json()["id"]

        send_resp = await auth_client.post(
            "/api/messages",
            json={"receiver_id": other_id, "content": "Hello there!"},
        )
        assert send_resp.status_code == 201
        assert send_resp.json()["content"] == "Hello there!"

        conv_resp = await auth_client.get(f"/api/messages/{other_id}")
        assert conv_resp.status_code == 200
        assert len(conv_resp.json()) >= 1

        list_resp = await auth_client.get("/api/messages")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

    async def test_mark_messages_read(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        other_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        other_id = other_me.json()["id"]

        await auth_client.post(
            "/api/messages",
            json={"receiver_id": other_id, "content": "Read me"},
        )

        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]

        mark_resp = await auth_client.post(
            f"/api/messages/{my_id}/read",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        assert mark_resp.status_code == 200


class TestNotification:
    async def test_list_notifications(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/notifications")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_mark_all_read(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/notifications/read-all")
        assert resp.status_code == 200


class TestSearch:
    async def test_search_users(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/search/users", params={"q": "test"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_search_hashtags(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/posts",
            json={"content": "Check out #python!", "image_url": None},
        )
        resp = await auth_client.get("/api/search/hashtags", params={"q": "python"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_posts_by_hashtag(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/posts",
            json={"content": "More #fastapi content", "image_url": None},
        )
        resp = await auth_client.get("/api/search/posts/hashtag/fastapi")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1
