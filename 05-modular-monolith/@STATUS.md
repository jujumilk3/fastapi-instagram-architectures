# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Full Modular Monolith Architecture Implemented + Tested
- 11 vertical modules: auth, user, post, comment, like, follow, feed, story, messaging, notification, search
- Shared infrastructure: database, security, base model, event bus
- Each module has own models, service, schemas, router
- 30 API tests passing
- bcrypt<5.0.0 pinned for passlib compatibility

## Code Location Map

### Shared (`src/modular_monolith/shared/`)
- `config.py`, `database.py`, `security.py`, `base_model.py`, `event_bus.py`

### Modules (`src/modular_monolith/modules/`)
- `auth/` - User model, auth service, auth router
- `user/` - User profile service + router (cross-module query on auth.models.User)
- `post/` - Post + PostHashtag + Hashtag models, post service + router
- `comment/` - Comment model, service, router
- `like/` - Like model, service, router
- `follow/` - Follow model, service, router
- `feed/` - Feed service + router (aggregates from follow + post)
- `story/` - Story model, service, router
- `messaging/` - Message model, service, router
- `notification/` - Notification model, service, router
- `search/` - Search service + router (queries across user, hashtag, post)

### Tests (`tests/`)
- `conftest.py` - Test DB, fixtures
- `test_api.py` - 30 tests across 11 test classes

## How to Work on This

```bash
cd 05-modular-monolith
uv sync
uv run uvicorn modular_monolith.main:app --reload
uv run pytest tests/ -v
```

## Architecture Decisions

- Vertical slicing by feature/domain (not horizontal layers)
- Each module exposes public API via `__init__.py`
- Inter-module communication through direct imports (could be replaced with event bus)
- Shared infrastructure kept minimal
- Each module theoretically separable into a microservice
