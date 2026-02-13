# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Vertical Slice Architecture Implemented
- ✅ Full Instagram clone API with 30 passing tests
- ✅ Mediator pattern for request dispatching (`src/vertical_slice/shared/mediator.py`)
- ✅ 32 self-contained feature handlers in `src/vertical_slice/features/`
- ✅ 10 ORM models in `src/vertical_slice/models/tables.py`
- ✅ Thin API routers that only handle HTTP concerns (`src/vertical_slice/api/routers.py`)
- ✅ All endpoints match the shared API contract across architectures

## Next Actions (Priority Order)

1. **[LOW]** Add pagination metadata to list endpoints
2. **[LOW]** Add input validation for edge cases (empty strings, max lengths)

## Code Location Map

### Shared Infrastructure (`src/vertical_slice/shared/`)
- `database.py` - async engine, sessionmaker, get_db dependency
- `security.py` - JWT + bcrypt (hash, verify, create/decode token, get_current_user_id)
- `mediator.py` - Mediator class: register(request_type, handler), send(request)

### Models (`src/vertical_slice/models/`)
- `base.py` - Base, TimestampMixin (timezone-aware DateTime)
- `tables.py` - All 10 ORM models (User, Post, Comment, Like, Follow, Story, Message, Notification, Hashtag, PostHashtag)

### Feature Handlers (`src/vertical_slice/features/`)
- `auth/` - register, login, get_me (3 slices)
- `user/` - get_profile, update_profile, get_user_posts, get_followers, get_following (5 slices)
- `post/` - create_post, get_post, delete_post (3 slices)
- `comment/` - create_comment, get_comments, delete_comment (3 slices)
- `like/` - toggle_like (1 slice)
- `follow/` - follow_user, unfollow_user (2 slices)
- `feed/` - get_feed (1 slice)
- `story/` - create_story, get_my_stories, get_story_feed, delete_story (4 slices)
- `message/` - send_message, get_conversations, get_conversation, mark_messages_read (4 slices)
- `notification/` - get_notifications, mark_notification_read, mark_all_read (3 slices)
- `search/` - search_users, search_hashtags, get_posts_by_hashtag (3 slices)

### API Layer (`src/vertical_slice/api/`)
- `schemas.py` - Pydantic request/response DTOs for the API boundary
- `routers.py` - Thin routers creating Request objects and sending via mediator
- `dependencies.py` - get_current_user_id, get_mediator

### Application Entry (`src/vertical_slice/main.py`)
- Handler registration, lifespan, router inclusion

### Tests (`tests/`)
- `conftest.py` - Test DB setup, client/auth fixtures
- `test_api.py` - 30 tests covering all endpoints

## How to Work on This

### Setup
```bash
cd 07-vertical-slice
uv sync
```

### Run Server
```bash
uv run uvicorn vertical_slice.main:app --reload
```

### Run Tests
```bash
uv run pytest tests/ -v
```

### Current Tech Stack
- Python 3.11+, FastAPI, SQLAlchemy 2.0 async, aiosqlite
- Pydantic v2, python-jose (JWT), passlib[bcrypt]
- uv package manager, hatchling build system (src/ layout)

## Known Issues

None

## Architecture Decisions

- **Vertical Slice**: Each feature is a self-contained slice (Request DTO -> Handler -> Response DTO)
- **Mediator pattern**: Dict-based dispatcher routes requests to handlers by type
- **No shared service layer**: Each handler does its own DB queries directly
- **Organized by use case** not by domain module (differs from Modular Monolith)
- **Thin API routers**: Only parse HTTP request, create Request object, call mediator, return response
- Singular snake_case table names, timezone-aware DateTime columns
