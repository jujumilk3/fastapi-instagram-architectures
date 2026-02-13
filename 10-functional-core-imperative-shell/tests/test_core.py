from datetime import datetime, timedelta, timezone

from functional_core.core.auth import create_token_payload, validate_credentials, validate_registration
from functional_core.core.comment import can_delete_comment, validate_comment
from functional_core.core.follow import validate_follow
from functional_core.core.like import determine_like_action
from functional_core.core.message import validate_message
from functional_core.core.notification import create_notification_data
from functional_core.core.post import build_post_response, can_delete_post, extract_hashtags, validate_post
from functional_core.core.search import matches_query
from functional_core.core.story import is_story_expired, validate_story


class TestAuthCore:
    def test_validate_registration_success(self):
        result = validate_registration("testuser", "a@b.com", [], [])
        assert result.success is True

    def test_validate_registration_short_username(self):
        result = validate_registration("ab", "a@b.com", [], [])
        assert result.success is False
        assert "Username" in result.error

    def test_validate_registration_duplicate_email(self):
        result = validate_registration("testuser", "a@b.com", ["a@b.com"], [])
        assert result.success is False
        assert "Email" in result.error

    def test_validate_registration_duplicate_username(self):
        result = validate_registration("testuser", "a@b.com", [], ["testuser"])
        assert result.success is False
        assert "Username" in result.error

    def test_create_token_payload(self):
        payload = create_token_payload(42)
        assert payload == {"sub": "42"}

    def test_validate_credentials_success(self):
        result = validate_credentials("hashed", True)
        assert result.success is True

    def test_validate_credentials_failure(self):
        result = validate_credentials("hashed", False)
        assert result.success is False


class TestPostCore:
    def test_validate_post_with_content(self):
        assert validate_post("Hello", None).success is True

    def test_validate_post_empty(self):
        assert validate_post(None, None).success is False

    def test_extract_hashtags(self):
        assert extract_hashtags("Hello #world #python") == ["world", "python"]

    def test_extract_hashtags_none(self):
        assert extract_hashtags(None) == []

    def test_can_delete_post_owner(self):
        assert can_delete_post(1, 1) is True

    def test_can_delete_post_not_owner(self):
        assert can_delete_post(1, 2) is False

    def test_build_post_response(self):
        resp = build_post_response(1, 2, "user", "content", None, 5, 3, "2024-01-01")
        assert resp["id"] == 1
        assert resp["like_count"] == 5


class TestCommentCore:
    def test_validate_comment_success(self):
        assert validate_comment("Nice!").success is True

    def test_validate_comment_empty(self):
        assert validate_comment("").success is False

    def test_can_delete_comment(self):
        assert can_delete_comment(1, 1) is True
        assert can_delete_comment(1, 2) is False


class TestLikeCore:
    def test_determine_like_action_add(self):
        assert determine_like_action(False) == "add"

    def test_determine_like_action_remove(self):
        assert determine_like_action(True) == "remove"


class TestFollowCore:
    def test_validate_follow_success(self):
        assert validate_follow(1, 2).success is True

    def test_validate_follow_self(self):
        result = validate_follow(1, 1)
        assert result.success is False


class TestStoryCore:
    def test_validate_story_with_content(self):
        assert validate_story(None, "My story").success is True

    def test_validate_story_empty(self):
        assert validate_story(None, None).success is False

    def test_is_story_expired_fresh(self):
        assert is_story_expired(datetime.now(timezone.utc)) is False

    def test_is_story_expired_old(self):
        old = datetime.now(timezone.utc) - timedelta(hours=25)
        assert is_story_expired(old) is True


class TestMessageCore:
    def test_validate_message_success(self):
        assert validate_message("Hello").success is True

    def test_validate_message_empty(self):
        assert validate_message("").success is False


class TestNotificationCore:
    def test_create_like_notification(self):
        data = create_notification_data("like", 1, 2, 10)
        assert data["type"] == "like"
        assert data["actor_id"] == 1
        assert data["user_id"] == 2
        assert data["reference_id"] == 10

    def test_create_follow_notification(self):
        data = create_notification_data("follow", 1, 2)
        assert data["type"] == "follow"
        assert data["reference_id"] is None


class TestSearchCore:
    def test_matches_query(self):
        assert matches_query("testuser", "test") is True

    def test_matches_query_no_match(self):
        assert matches_query("testuser", "xyz") is False
