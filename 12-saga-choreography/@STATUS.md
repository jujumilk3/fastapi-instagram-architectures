# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Full Saga Choreography Architecture Implemented
- ✅ Complete project structure with pyproject.toml and uv package management
- ✅ Shared infrastructure: database, security (JWT/bcrypt), event bus, saga executor
- ✅ SagaLog ORM model persists every saga step (saga_id, saga_type, step_name, status)
- ✅ 7 sagas: create_post, delete_post, like_post, follow_user, send_message, create_story, comment
- ✅ Each saga has compensating actions for rollback on failure
- ✅ Choreography event handlers for cross-domain side effects (hashtag extraction, notifications)
- ✅ All 24 API endpoints matching the standard Instagram clone interface
- ✅ 39 tests passing: auth(6), user(3), post(4), comment(2), like(1), follow(3), feed(1), story(3), message(2), notification(5), search(3), saga infrastructure(6)

## Code Location Map

### Shared (`src/saga_choreography/shared/`)
- `database.py` - Async SQLAlchemy engine, session factory, get_db
- `security.py` - JWT token creation/validation, bcrypt password hashing
- `event_bus.py` - In-memory pub/sub EventBus (subscribe, publish, clear)
- `saga.py` - SagaStep dataclass, SagaExecutor (execute steps, compensate on failure, log to SagaLog)

### Models (`src/saga_choreography/models/`)
- `base.py` - TimestampMixin with timezone-aware created_at
- `tables.py` - All ORM models: User, Post, Comment, Like, Follow, Story, Message, Notification, Hashtag, PostHashtag, SagaLog

### Services (`src/saga_choreography/services/`)
- Atomic database operations used by sagas and direct queries
- `auth_service.py` - register, login (no saga needed)
- `user_service.py` - get_user_by_id, get_user_profile, update_user
- `post_service.py` - CRUD + queries (get_post, get_user_posts, get_post_comments)
- `comment_service.py` - create/delete comment
- `like_service.py` - add_like, remove_like, toggle_like
- `follow_service.py` - create_follow, delete_follow
- `feed_service.py` - get_feed
- `story_service.py` - CRUD + queries
- `message_service.py` - CRUD + conversations queries
- `notification_service.py` - CRUD + mark read
- `search_service.py` - search users, hashtags, posts by hashtag
- `hashtag_service.py` - extract_and_save, delete_post_hashtags

### Sagas (`src/saga_choreography/sagas/`)
- `create_post_saga.py` - create_post -> extract_hashtags (compensate: delete_hashtags -> delete_post)
- `delete_post_saga.py` - delete_comments -> delete_likes -> delete_hashtags -> delete_post
- `like_post_saga.py` - toggle_like -> create_notification
- `follow_user_saga.py` - create_follow -> create_notification (compensate both)
- `send_message_saga.py` - create_message -> create_notification (compensate both)
- `create_story_saga.py` - create_story (compensate: delete_story)
- `comment_saga.py` - create_comment -> create_notification (compensate both)

### Choreography (`src/saga_choreography/choreography/`)
- `handlers.py` - Event handlers: on_post_created, on_post_liked, on_comment_added, on_user_followed

### API (`src/saga_choreography/api/`)
- `schemas.py` - Pydantic v2 request/response models
- `dependencies.py` - OAuth2 token extraction, session dependency
- `routers.py` - All 24 API endpoint handlers using sagas for multi-step writes

### Tests (`tests/`)
- `conftest.py` - Test DB setup, client fixtures, auth fixtures
- `test_api.py` - 39 tests covering all endpoints + saga infrastructure

## How to Work on This

### Setup
```bash
cd 12-saga-choreography
uv sync
```

### Run Server
```bash
uv run uvicorn saga_choreography.main:app --reload
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

- Sagas handle multi-step writes; simple reads/auth use services directly
- SagaExecutor logs every step to SagaLog table for auditability
- Compensation runs in reverse order on failure
- Choreography handlers are event-driven side effects (hashtag extraction, notifications)
- EventBus is in-memory (wired at app lifespan startup)
- DB is source of truth (no event sourcing)
