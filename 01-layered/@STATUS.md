# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Full Layered Architecture Implemented + Tested
- All models, repositories, services, schemas, and API routers
- 29 API tests passing
- bcrypt<5.0.0 pinned for passlib compatibility
- selectinload added for async relationship loading

## Code Location Map

### Models (`src/layered/models/`)
- `base.py` - DeclarativeBase + TimestampMixin
- `user.py`, `post.py`, `comment.py`, `like.py`, `follow.py`
- `story.py`, `message.py`, `notification.py`, `hashtag.py`

### Repositories (`src/layered/repositories/`)
- One per model: user, post, comment, like, follow, story, message, notification, hashtag

### Services (`src/layered/services/`)
- auth, user, post, comment, like, follow, feed, story, message, notification, search

### Schemas (`src/layered/schemas/`)
- user, post, comment, story, message, notification, hashtag

### API Routers (`src/layered/api/`)
- auth, user, post, follow, feed, story, message, notification, search

### Tests (`tests/`)
- `conftest.py` - Test DB, fixtures (client, auth_client, second_user_token)
- `test_api.py` - 29 tests across 11 test classes

## How to Work on This

```bash
cd 01-layered
uv sync
uv run uvicorn layered.main:app --reload
uv run pytest tests/ -v
```

## Architecture Decisions

- Strict horizontal layering: API -> Service -> Repository -> Model
- Anemic ORM models (data only, no behavior)
- All table names singular snake_case
- All datetime columns timezone-aware
