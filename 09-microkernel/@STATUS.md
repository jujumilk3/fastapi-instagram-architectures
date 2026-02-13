# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Microkernel Architecture Implemented
- ✅ Created complete microkernel (plugin) architecture for Instagram clone
- ✅ Core infrastructure: `src/microkernel/core/` (database, security, plugin ABC, registry, base_model, schemas)
- ✅ 9 plugins implemented: auth, user, post, follow, feed, story, message, notification, search
- ✅ Each plugin implements `Plugin` ABC with `name` property and `register(app)` method
- ✅ `PluginRegistry` discovers and registers all plugins dynamically
- ✅ All 30 tests passing
- ✅ All API endpoints matching specification

## Next Actions (Priority Order)

1. **[LOW]** Add plugin-level health checks or metadata endpoints
2. **[LOW]** Add dynamic plugin enable/disable at runtime

## Code Location Map

### Core (`src/microkernel/core/`)
- `plugin.py` - Plugin ABC (name property + register method)
- `registry.py` - PluginRegistry (register, get_all, startup)
- `database.py` - Async SQLAlchemy engine, session, get_db dependency
- `security.py` - JWT + bcrypt auth infrastructure
- `base_model.py` - Base declarative class + TimestampMixin
- `schemas.py` - Shared TokenResponse schema

### Plugins (`src/microkernel/plugins/`)
- `__init__.py` - PLUGIN_LIST for discovery
- `auth/` - User model, registration, login, JWT tokens
- `user/` - Profile, update, followers/following
- `post/` - Post CRUD, comments, likes, hashtags (Comment/Like/Hashtag models here)
- `follow/` - Follow/unfollow with notification creation
- `feed/` - Feed aggregation from followed users
- `story/` - Story CRUD with 24h expiry
- `message/` - Direct messaging, conversations, mark-read
- `notification/` - Notification listing, mark-read
- `search/` - User search, hashtag search, posts by hashtag

### Main (`src/microkernel/main.py`)
- Creates FastAPI app, iterates PLUGIN_LIST, registers via PluginRegistry

### Tests (`tests/`)
- `conftest.py` - Test DB setup, client fixtures, auth helpers
- `test_api.py` - 30 tests covering all endpoints

## How to Work on This

### Setup
```bash
cd 09-microkernel
uv sync
```

### Run
```bash
uv run uvicorn microkernel.main:app --reload
```

### Run Tests
```bash
uv run pytest tests/ -v
```

### Current Tech Stack
- Python 3.11+, FastAPI, SQLAlchemy 2.0 async, aiosqlite
- Pydantic v2, python-jose (JWT), passlib[bcrypt]
- uv package manager, hatchling build system

## Known Issues

None

## Architecture Decisions

- Microkernel pattern: minimal core with plugin-based feature registration
- Each plugin self-registers via `Plugin` ABC and `PluginRegistry`
- Core knows nothing about specific features; plugins bring their own models/routes/services
- Cross-plugin DB queries allowed (e.g., feed reads follow + post tables)
- Comment, Like, Hashtag models live in post plugin since their routes are under `/api/posts/`
- Singular snake_case table names, timezone-aware DateTime columns
