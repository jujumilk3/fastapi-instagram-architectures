# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Full Implementation Complete
- ✅ Functional Core, Imperative Shell architecture implemented
- ✅ Pure core functions (no IO imports): auth, post, comment, like, follow, story, message, notification, search
- ✅ Imperative shell handlers: fetch from DB -> call pure functions -> persist results
- ✅ All 29 API endpoints matching other architectures
- ✅ 60 tests passing (31 pure core unit tests + 29 API integration tests)
- ✅ Singular snake_case table names, timezone-aware DateTime columns

## Next Actions (Priority Order)

1. **[LOW]** Add input validation using core functions in more handlers
2. **[LOW]** Add pagination metadata to list endpoints

## Code Location Map

### Pure Core (`src/functional_core/core/`)
- `types.py` - Result dataclass (frozen, immutable)
- `auth.py` - validate_registration, create_token_payload, validate_credentials
- `post.py` - validate_post, extract_hashtags, can_delete_post, build_post_response
- `comment.py` - validate_comment, can_delete_comment
- `like.py` - determine_like_action
- `follow.py` - validate_follow
- `story.py` - validate_story, is_story_expired, get_story_cutoff
- `message.py` - validate_message
- `notification.py` - create_notification_data
- `search.py` - matches_query

### Imperative Shell (`src/functional_core/shell/`)
- `database.py` - async engine, sessionmaker, get_db
- `security.py` - JWT encode/decode, bcrypt hash/verify
- `models.py` - All SQLAlchemy ORM models (User, Post, Comment, Like, Follow, Hashtag, PostHashtag, Story, Message, Notification)
- `handlers/auth_handler.py` - register_user, login_user, get_current_user
- `handlers/user_handler.py` - get_profile, update_profile, get_followers, get_following
- `handlers/post_handler.py` - create_post, get_post, get_posts_by_author, delete_post
- `handlers/comment_handler.py` - create_comment, get_comments_by_post, delete_comment
- `handlers/like_handler.py` - toggle_like
- `handlers/follow_handler.py` - follow_user, unfollow_user
- `handlers/feed_handler.py` - get_feed
- `handlers/story_handler.py` - create_story, get_my_stories, get_story_feed, delete_story
- `handlers/message_handler.py` - send_message, get_conversations, get_conversation, mark_messages_read
- `handlers/notification_handler.py` - get_notifications, mark_notification_read, mark_all_notifications_read
- `handlers/search_handler.py` - search_users, search_hashtags, get_posts_by_hashtag

### API Layer (`src/functional_core/api/`)
- `schemas.py` - All Pydantic request/response models
- `dependencies.py` - get_current_user_id (OAuth2 + JWT)
- `routers.py` - All route definitions calling shell handlers

### Tests (`tests/`)
- `conftest.py` - Test fixtures (client, auth_client, second_user_token)
- `test_core.py` - 31 pure function unit tests (no mocks needed)
- `test_api.py` - 29 API integration tests

## How to Work on This

### Setup
```bash
cd 10-functional-core-imperative-shell
uv sync
```

### Run
```bash
uv run uvicorn functional_core.main:app --reload
```

### Run Tests
```bash
uv run pytest tests/ -v
```

### Current Tech Stack
- Python 3.11+, FastAPI, SQLAlchemy 2.0 async, aiosqlite
- Pydantic v2, python-jose (JWT), passlib[bcrypt]
- uv package manager, hatchling build system

## Architecture Decisions

- **Pure functions in core/**: No imports of SQLAlchemy, FastAPI, or any IO library. Only stdlib + own types.
- **Shell handlers do all IO**: DB queries, password hashing, JWT creation all happen in shell.
- **No repository pattern**: Shell handlers query the DB directly (simpler than Clean/Hexagonal).
- **No dependency injection for IO**: Shell orchestrates everything explicitly.
- **Result type**: Frozen dataclass for pure function return values.
- Core tests require zero mocks - they test pure input->output transformations.
