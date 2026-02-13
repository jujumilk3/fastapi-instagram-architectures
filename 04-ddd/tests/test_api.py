import pytest
from httpx import AsyncClient


class TestAuth:
    async def test_register(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
                "full_name": "New User",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["full_name"] == "New User"

    async def test_register_duplicate_email(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/api/auth/register",
            json={
                "username": "another",
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert resp.status_code in (400, 409)

    async def test_login(self, client: AsyncClient, auth_client: AsyncClient):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_invalid_credentials(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "wrong@example.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    async def test_me(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    async def test_me_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401


class TestUser:
    async def test_get_profile(self, auth_client: AsyncClient):
        me = await auth_client.get("/api/auth/me")
        user_id = me.json()["id"]
        resp = await auth_client.get(f"/api/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"
        assert "post_count" in resp.json()

    async def test_update_me(self, auth_client: AsyncClient):
        resp = await auth_client.put(
            "/api/users/me",
            json={"bio": "Hello world", "full_name": "Test User Updated"},
        )
        assert resp.status_code == 200
        assert resp.json()["bio"] == "Hello world"
        assert resp.json()["full_name"] == "Test User Updated"

    async def test_nonexistent_user(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/users/99999")
        assert resp.status_code == 404


class TestPost:
    async def test_create_post(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/api/posts",
            json={"content": "My first post #hello", "image_url": "https://img.com/1.jpg"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "My first post #hello"
        assert data["author_username"] == "testuser"

    async def test_get_post(self, auth_client: AsyncClient):
        create_resp = await auth_client.post(
            "/api/posts",
            json={"content": "Get this post"},
        )
        post_id = create_resp.json()["id"]
        resp = await auth_client.get(f"/api/posts/{post_id}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "Get this post"

    async def test_delete_post(self, auth_client: AsyncClient):
        create_resp = await auth_client.post(
            "/api/posts",
            json={"content": "To be deleted"},
        )
        post_id = create_resp.json()["id"]
        resp = await auth_client.delete(f"/api/posts/{post_id}")
        assert resp.status_code == 204

        get_resp = await auth_client.get(f"/api/posts/{post_id}")
        assert get_resp.status_code == 404

    async def test_get_user_posts(self, auth_client: AsyncClient):
        me = await auth_client.get("/api/auth/me")
        user_id = me.json()["id"]
        resp = await auth_client.get(f"/api/users/{user_id}/posts")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestComment:
    async def test_create_and_get_comments(self, auth_client: AsyncClient):
        post_resp = await auth_client.post(
            "/api/posts",
            json={"content": "Post for comments"},
        )
        post_id = post_resp.json()["id"]

        comment_resp = await auth_client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "Nice post!"},
        )
        assert comment_resp.status_code == 201
        assert comment_resp.json()["content"] == "Nice post!"

        list_resp = await auth_client.get(f"/api/posts/{post_id}/comments")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

    async def test_delete_comment(self, auth_client: AsyncClient):
        post_resp = await auth_client.post(
            "/api/posts",
            json={"content": "Post for comment deletion"},
        )
        post_id = post_resp.json()["id"]

        comment_resp = await auth_client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "Will be deleted"},
        )
        comment_id = comment_resp.json()["id"]

        del_resp = await auth_client.delete(f"/api/posts/comments/{comment_id}")
        assert del_resp.status_code == 204


class TestLike:
    async def test_toggle_like(self, auth_client: AsyncClient):
        post_resp = await auth_client.post(
            "/api/posts",
            json={"content": "Likeable post"},
        )
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
    async def test_follow_and_unfollow(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        other_resp = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        other_id = other_resp.json()["id"]

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


class TestFeed:
    async def test_get_feed(self, auth_client: AsyncClient, second_user_token: str):
        other_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        other_id = other_me.json()["id"]

        await auth_client.post(
            "/api/posts",
            json={"content": "Other user post"},
            headers={"Authorization": f"Bearer {second_user_token}"},
        )

        await auth_client.post(f"/api/follow/{other_id}")

        resp = await auth_client.get("/api/feed")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestStory:
    async def test_create_and_get_stories(self, auth_client: AsyncClient):
        create_resp = await auth_client.post(
            "/api/stories",
            json={"content": "My story", "image_url": "https://img.com/story.jpg"},
        )
        assert create_resp.status_code == 201
        assert create_resp.json()["content"] == "My story"

        list_resp = await auth_client.get("/api/stories")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

    async def test_story_feed(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/stories/feed")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_delete_story(self, auth_client: AsyncClient):
        create_resp = await auth_client.post(
            "/api/stories",
            json={"content": "Delete me"},
        )
        story_id = create_resp.json()["id"]
        del_resp = await auth_client.delete(f"/api/stories/{story_id}")
        assert del_resp.status_code == 204


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

    async def test_mark_messages_read(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        me_resp = await auth_client.get("/api/auth/me")
        my_id = me_resp.json()["id"]

        other_client_headers = {"Authorization": f"Bearer {second_user_token}"}
        await auth_client.post(
            "/api/messages",
            json={"receiver_id": my_id, "content": "Read me"},
            headers=other_client_headers,
        )

        other_me = await auth_client.get("/api/auth/me", headers=other_client_headers)
        other_id = other_me.json()["id"]

        resp = await auth_client.post(f"/api/messages/{other_id}/read")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestNotification:
    async def test_list_notifications(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/notifications")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_mark_all_read(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/notifications/read-all")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestSearch:
    async def test_search_users(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/search/users", params={"q": "test"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert any(u["username"] == "testuser" for u in resp.json())

    async def test_search_hashtags(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/posts",
            json={"content": "Searching #findme tag"},
        )
        resp = await auth_client.get("/api/search/hashtags", params={"q": "find"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_posts_by_hashtag(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/posts",
            json={"content": "Tagged #unique123"},
        )
        resp = await auth_client.get("/api/search/posts/hashtag/unique123")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1
