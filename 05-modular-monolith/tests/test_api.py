import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAuth:
    async def test_register(self, client: AsyncClient):
        resp = await client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "pass123",
            "full_name": "New User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True

    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "username": "dupeuser1",
            "email": "dupe@example.com",
            "password": "pass123",
        })
        resp = await client.post("/api/auth/register", json={
            "username": "dupeuser2",
            "email": "dupe@example.com",
            "password": "pass123",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    async def test_login(self, client: AsyncClient):
        await client.post("/api/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "pass123",
        })
        resp = await client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "pass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        resp = await client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrong",
        })
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
        assert "following_count" in data

    async def test_update_me(self, auth_client: AsyncClient):
        resp = await auth_client.put("/api/users/me", json={
            "bio": "Hello world",
            "full_name": "Updated Name",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["bio"] == "Hello world"
        assert data["full_name"] == "Updated Name"

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
        assert data["like_count"] == 0
        assert data["comment_count"] == 0

    async def test_get_post(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/posts", json={
            "content": "Get me post",
        })
        post_id = create_resp.json()["id"]
        resp = await auth_client.get(f"/api/posts/{post_id}")
        assert resp.status_code == 200
        assert resp.json()["content"] == "Get me post"

    async def test_delete_post(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/posts", json={
            "content": "Delete me",
        })
        post_id = create_resp.json()["id"]
        resp = await auth_client.delete(f"/api/posts/{post_id}")
        assert resp.status_code == 204

        resp = await auth_client.get(f"/api/posts/{post_id}")
        assert resp.status_code == 404

    async def test_delete_post_not_owner(self, auth_client: AsyncClient, second_user_token: str):
        create_resp = await auth_client.post("/api/posts", json={
            "content": "Not yours to delete",
        })
        post_id = create_resp.json()["id"]
        resp = await auth_client.delete(
            f"/api/posts/{post_id}",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        assert resp.status_code == 403


class TestComment:
    async def test_create_and_get_comments(self, auth_client: AsyncClient):
        post_resp = await auth_client.post("/api/posts", json={"content": "Commentable post"})
        post_id = post_resp.json()["id"]

        comment_resp = await auth_client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "Nice post!"},
        )
        assert comment_resp.status_code == 201
        assert comment_resp.json()["content"] == "Nice post!"

        list_resp = await auth_client.get(f"/api/posts/{post_id}/comments")
        assert list_resp.status_code == 200
        comments = list_resp.json()
        assert len(comments) >= 1
        assert any(c["content"] == "Nice post!" for c in comments)

    async def test_delete_comment(self, auth_client: AsyncClient):
        post_resp = await auth_client.post("/api/posts", json={"content": "Post for comment deletion"})
        post_id = post_resp.json()["id"]

        comment_resp = await auth_client.post(
            f"/api/posts/{post_id}/comments",
            json={"content": "To be deleted"},
        )
        comment_id = comment_resp.json()["id"]

        del_resp = await auth_client.delete(f"/api/posts/comments/{comment_id}")
        assert del_resp.status_code == 204


class TestLike:
    async def test_toggle_like(self, auth_client: AsyncClient):
        post_resp = await auth_client.post("/api/posts", json={"content": "Likeable post"})
        post_id = post_resp.json()["id"]

        like_resp = await auth_client.post(f"/api/posts/{post_id}/likes")
        assert like_resp.status_code == 200
        data = like_resp.json()
        assert data["liked"] is True
        assert data["like_count"] == 1

        unlike_resp = await auth_client.post(f"/api/posts/{post_id}/likes")
        assert unlike_resp.status_code == 200
        data = unlike_resp.json()
        assert data["liked"] is False
        assert data["like_count"] == 0


class TestFollow:
    async def test_follow_and_unfollow(self, auth_client: AsyncClient, second_user_token: str):
        second_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        second_id = second_me.json()["id"]

        follow_resp = await auth_client.post(f"/api/follow/{second_id}")
        assert follow_resp.status_code == 200
        assert follow_resp.json()["following"] is True

        unfollow_resp = await auth_client.delete(f"/api/follow/{second_id}")
        assert unfollow_resp.status_code == 200
        assert unfollow_resp.json()["following"] is False

    async def test_cannot_follow_self(self, auth_client: AsyncClient):
        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]
        resp = await auth_client.post(f"/api/follow/{my_id}")
        assert resp.status_code == 400
        assert "yourself" in resp.json()["detail"].lower()

    async def test_followers_and_following_lists(
        self, auth_client: AsyncClient, second_user_token: str
    ):
        other_resp = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        other_id = other_resp.json()["id"]

        await auth_client.post(f"/api/follow/{other_id}")

        me = await auth_client.get("/api/auth/me")
        my_id = me.json()["id"]

        followers_resp = await auth_client.get(f"/api/users/{other_id}/followers")
        assert followers_resp.status_code == 200

        following_resp = await auth_client.get(f"/api/users/{my_id}/following")
        assert following_resp.status_code == 200

        await auth_client.delete(f"/api/follow/{other_id}")


class TestFeed:
    async def test_get_feed(self, auth_client: AsyncClient, second_user_token: str):
        second_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        second_id = second_me.json()["id"]

        await auth_client.post(f"/api/follow/{second_id}")

        transport = auth_client._transport
        async with AsyncClient(transport=transport, base_url="http://testserver") as second_client:
            second_client.headers["Authorization"] = f"Bearer {second_user_token}"
            await second_client.post("/api/posts", json={"content": "Feed post from second user"})

        resp = await auth_client.get("/api/feed")
        assert resp.status_code == 200
        posts = resp.json()
        assert isinstance(posts, list)


class TestStory:
    async def test_create_and_get_stories(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/stories", json={
            "image_url": "https://example.com/story.jpg",
            "content": "My story",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "My story"
        assert data["image_url"] == "https://example.com/story.jpg"

        list_resp = await auth_client.get("/api/stories")
        assert list_resp.status_code == 200
        stories = list_resp.json()
        assert len(stories) >= 1

    async def test_story_feed(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/stories/feed")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_delete_story(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/stories", json={"content": "Delete this story"})
        story_id = create_resp.json()["id"]

        del_resp = await auth_client.delete(f"/api/stories/{story_id}")
        assert del_resp.status_code == 204


class TestMessage:
    async def test_send_and_get_messages(self, auth_client: AsyncClient, second_user_token: str):
        second_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        second_id = second_me.json()["id"]

        resp = await auth_client.post("/api/messages", json={
            "receiver_id": second_id,
            "content": "Hello there!",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "Hello there!"
        assert data["is_read"] is False

        conv_resp = await auth_client.get(f"/api/messages/{second_id}")
        assert conv_resp.status_code == 200
        messages = conv_resp.json()
        assert len(messages) >= 1
        assert any(m["content"] == "Hello there!" for m in messages)

    async def test_mark_messages_read(self, auth_client: AsyncClient, second_user_token: str):
        me_resp = await auth_client.get("/api/auth/me")
        my_id = me_resp.json()["id"]

        second_me = await auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {second_user_token}"},
        )
        second_id = second_me.json()["id"]

        transport = auth_client._transport
        async with AsyncClient(transport=transport, base_url="http://testserver") as second_client:
            second_client.headers["Authorization"] = f"Bearer {second_user_token}"
            await second_client.post("/api/messages", json={
                "receiver_id": my_id,
                "content": "Read this!",
            })

        resp = await auth_client.post(f"/api/messages/{second_id}/read")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_list_conversations(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/messages")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestNotification:
    async def test_list_notifications(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/notifications")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_mark_all_read(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/notifications/read-all")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

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
        users = resp.json()
        assert isinstance(users, list)
        assert any(u["username"] == "testuser" for u in users)

    async def test_search_hashtags(self, auth_client: AsyncClient):
        await auth_client.post("/api/posts", json={"content": "Searchable #python"})

        resp = await auth_client.get("/api/search/hashtags", params={"q": "python"})
        assert resp.status_code == 200
        tags = resp.json()
        assert isinstance(tags, list)
        assert any(t["name"] == "python" for t in tags)

    async def test_posts_by_hashtag(self, auth_client: AsyncClient):
        await auth_client.post("/api/posts", json={"content": "Tagged #findme"})

        resp = await auth_client.get("/api/search/posts/hashtag/findme")
        assert resp.status_code == 200
        posts = resp.json()
        assert isinstance(posts, list)
        assert len(posts) >= 1
        assert any("findme" in (p["content"] or "") for p in posts)
