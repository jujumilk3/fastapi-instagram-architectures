import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAuth:
    async def test_register(self, client: AsyncClient):
        resp = await client.post("/api/auth/register", json={
            "username": "newuser", "email": "new@example.com", "password": "pass123"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"

    async def test_register_duplicate_email(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/auth/register", json={
            "username": "another", "email": "test@example.com", "password": "pass123"
        })
        assert resp.status_code == 400

    async def test_login(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/auth/login", json={
            "email": "test@example.com", "password": "password123"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_invalid(self, client: AsyncClient):
        resp = await client.post("/api/auth/login", json={
            "email": "nonexistent@example.com", "password": "wrong"
        })
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
        assert "follower_count" in resp.json()

    async def test_update_me(self, auth_client: AsyncClient):
        resp = await auth_client.put("/api/users/me", json={"bio": "Hello world"})
        assert resp.status_code == 200
        assert resp.json()["bio"] == "Hello world"

    async def test_get_nonexistent_user(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/users/9999")
        assert resp.status_code == 404


class TestPost:
    async def test_create_post(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/posts", json={
            "content": "Hello #world", "image_url": "http://img.com/1.jpg"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "Hello #world"
        assert data["author_username"] == "testuser"

    async def test_get_post(self, auth_client: AsyncClient):
        create = await auth_client.post("/api/posts", json={"content": "Test post"})
        post_id = create.json()["id"]
        resp = await auth_client.get(f"/api/posts/{post_id}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "Test post"

    async def test_delete_post(self, auth_client: AsyncClient):
        create = await auth_client.post("/api/posts", json={"content": "To delete"})
        post_id = create.json()["id"]
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
        post = await auth_client.post("/api/posts", json={"content": "Post for comments"})
        post_id = post.json()["id"]

        resp = await auth_client.post(f"/api/posts/{post_id}/comments", json={"content": "Nice post!"})
        assert resp.status_code == 201
        assert resp.json()["content"] == "Nice post!"

        resp = await auth_client.get(f"/api/posts/{post_id}/comments")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_delete_comment(self, auth_client: AsyncClient):
        post = await auth_client.post("/api/posts", json={"content": "Post"})
        post_id = post.json()["id"]
        comment = await auth_client.post(f"/api/posts/{post_id}/comments", json={"content": "To delete"})
        comment_id = comment.json()["id"]
        resp = await auth_client.delete(f"/api/posts/comments/{comment_id}")
        assert resp.status_code == 204


class TestLike:
    async def test_toggle_like(self, auth_client: AsyncClient):
        post = await auth_client.post("/api/posts", json={"content": "Likeable"})
        post_id = post.json()["id"]

        resp = await auth_client.post(f"/api/posts/{post_id}/likes")
        assert resp.status_code == 200
        assert resp.json()["liked"] is True
        assert resp.json()["like_count"] == 1

        resp = await auth_client.post(f"/api/posts/{post_id}/likes")
        assert resp.json()["liked"] is False
        assert resp.json()["like_count"] == 0


class TestFollow:
    async def test_follow_and_unfollow(self, auth_client: AsyncClient, second_user_token: str):
        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]

        other_client = auth_client
        other_client.headers["Authorization"] = f"Bearer {second_user_token}"
        other_me = await other_client.get("/api/auth/me")
        other_id = other_me.json()["id"]

        # Restore original auth
        login = await auth_client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
        auth_client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"

        resp = await auth_client.post(f"/api/follow/{other_id}")
        assert resp.status_code == 200
        assert resp.json()["following"] is True

        resp = await auth_client.delete(f"/api/follow/{other_id}")
        assert resp.status_code == 200
        assert resp.json()["following"] is False

    async def test_cannot_follow_self(self, auth_client: AsyncClient):
        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]
        resp = await auth_client.post(f"/api/follow/{my_id}")
        assert resp.status_code == 400

    async def test_followers_and_following_lists(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        other_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        other_id = other_me.json()["id"]

        await auth_client.post(f"/api/follow/{other_id}")

        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]

        followers_resp = await auth_client.get(f"/api/users/{other_id}/followers")
        assert followers_resp.status_code == 200

        following_resp = await auth_client.get(f"/api/users/{my_id}/following")
        assert following_resp.status_code == 200

        await auth_client.delete(f"/api/follow/{other_id}")


class TestFeed:
    async def test_get_feed(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/feed")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestStory:
    async def test_create_and_get_stories(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/stories", json={"content": "My story"})
        assert resp.status_code == 201

        resp = await auth_client.get("/api/stories")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_story_feed(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/stories/feed")
        assert resp.status_code == 200

    async def test_delete_story(self, auth_client: AsyncClient):
        story = await auth_client.post("/api/stories", json={"content": "Temp story"})
        story_id = story.json()["id"]
        resp = await auth_client.delete(f"/api/stories/{story_id}")
        assert resp.status_code == 204


class TestMessage:
    async def test_send_and_get_messages(self, auth_client: AsyncClient, second_user_token: str):
        other_client = AsyncClient
        other = await auth_client.post("/api/auth/login", json={"email": "other@example.com", "password": "password123"})
        other_resp = other.json()

        # Get other user ID
        saved_auth = auth_client.headers.get("Authorization")
        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        other_me = await auth_client.get("/api/auth/me")
        other_id = other_me.json()["id"]
        auth_client.headers["Authorization"] = saved_auth

        resp = await auth_client.post("/api/messages", json={"receiver_id": other_id, "content": "Hello!"})
        assert resp.status_code == 201

        resp = await auth_client.get("/api/messages")
        assert resp.status_code == 200

        resp = await auth_client.get(f"/api/messages/{other_id}")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_mark_read(self, auth_client: AsyncClient, second_user_token: str):
        saved_auth = auth_client.headers.get("Authorization")
        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]

        # Send message from other user to test user
        auth_client.headers["Authorization"] = saved_auth
        orig_me = await auth_client.get("/api/auth/me")
        orig_id = orig_me.json()["id"]

        auth_client.headers["Authorization"] = f"Bearer {second_user_token}"
        await auth_client.post("/api/messages", json={"receiver_id": orig_id, "content": "Read me"})

        auth_client.headers["Authorization"] = saved_auth
        resp = await auth_client.post(f"/api/messages/{my_id}/read")
        assert resp.status_code == 200


class TestNotification:
    async def test_list_notifications(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/notifications")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_mark_all_read(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/notifications/read-all")
        assert resp.status_code == 200

    async def test_notification_created_on_follow(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        other_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        other_id = other_me.json()["id"]

        await auth_client.post(f"/api/follow/{other_id}")

        notif_resp = await auth_client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        assert notif_resp.status_code == 200
        notifications = notif_resp.json()
        follow_notifs = [n for n in notifications if n["type"] == "follow"]
        assert len(follow_notifs) >= 1

        await auth_client.delete(f"/api/follow/{other_id}")

    async def test_notification_created_on_like(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        post_resp = await auth_client.post(
            "/api/posts",
            json={"content": "Like for notif", "image_url": None},
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        post_id = post_resp.json()["id"]

        await auth_client.post(f"/api/posts/{post_id}/likes")

        notif_resp = await auth_client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        assert notif_resp.status_code == 200
        notifications = notif_resp.json()
        like_notifs = [n for n in notifications if n["type"] == "like"]
        assert len(like_notifs) >= 1

    async def test_mark_single_notification_read(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        notif_resp = await auth_client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        notifications = notif_resp.json()
        if notifications:
            notif_id = notifications[0]["id"]
            mark_resp = await auth_client.post(
                f"/api/notifications/{notif_id}/read",
                headers={"Authorization": f"Bearer {second_user_token}"},
            )
            assert mark_resp.status_code == 200


class TestSearch:
    async def test_search_users(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/search/users", params={"q": "test"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_search_hashtags(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/search/hashtags", params={"q": "world"})
        assert resp.status_code == 200

    async def test_posts_by_hashtag(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/search/posts/hashtag/world")
        assert resp.status_code == 200
