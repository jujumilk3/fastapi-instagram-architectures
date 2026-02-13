# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Clean Architecture Instagram Clone Implemented
- ✅ Full Clean Architecture project structure with 4 concentric layers
- ✅ Entities layer: pure Python dataclasses (User, Post, Comment, Like, Follow, Story, Message, Notification, Hashtag)
- ✅ Use Cases layer: 25 individual use case classes each with `execute()` method
- ✅ Interface Adapters layer: FastAPI controllers (routers), Pydantic schemas, SQLAlchemy gateway repositories
- ✅ Frameworks layer: database engine, JWT/bcrypt security, ORM models, DI wiring
- ✅ All 32 API endpoints verified working
- ✅ Dependencies flow inward: frameworks -> interface_adapters -> use_cases -> entities

## Code Location Map

### Entities (innermost) (`src/clean/entities/`)
- `user.py` - User dataclass
- `post.py` - Post, Comment, Like dataclasses
- `social.py` - Follow, Story, Message, Notification, Hashtag dataclasses

### Use Cases (`src/clean/use_cases/`)
- `interfaces/repositories.py` - All repository ABCs (9 repositories)
- `interfaces/security.py` - SecurityGateway ABC
- `auth/register.py, login.py, get_me.py` - Auth use cases
- `user/get_profile.py, update_profile.py, get_followers.py, get_following.py` - User use cases
- `post/create_post.py, get_post.py, get_user_posts.py, delete_post.py` - Post use cases
- `comment/create_comment.py, get_comments.py, delete_comment.py` - Comment use cases
- `like/toggle_like.py` - Like toggle use case
- `follow/follow_user.py, unfollow_user.py` - Follow use cases
- `feed/get_feed.py` - Feed use case
- `story/create_story.py, get_my_stories.py, get_story_feed.py, delete_story.py` - Story use cases
- `message/send_message.py, get_conversations.py, get_conversation.py, mark_read.py` - Message use cases
- `notification/get_notifications.py, mark_read.py, mark_all_read.py` - Notification use cases
- `search/search_users.py, search_hashtags.py, get_posts_by_hashtag.py` - Search use cases

### Interface Adapters (`src/clean/interface_adapters/`)
- `controllers/routers.py` - All FastAPI route handlers (9 routers)
- `gateways/repositories.py` - SQLAlchemy repository implementations (9 concrete repos)
- `schemas/schemas.py` - Pydantic request/response DTOs

### Frameworks (outermost) (`src/clean/frameworks/`)
- `database.py` - SQLAlchemy async engine and session factory
- `security.py` - JWT + bcrypt SecurityGateway implementation
- `models.py` - SQLAlchemy ORM models (10 tables, singular snake_case)
- `dependencies.py` - FastAPI dependency injection wiring

### Entry Point
- `src/clean/main.py` - FastAPI app with lifespan, router registration

## How to Work on This

### Setup
```bash
cd 03-clean
uv sync
```

### Run
```bash
uv run uvicorn clean.main:app --reload
```

### Verify Routes
```bash
uv run python -c "from clean.main import app; print([r.path for r in app.routes if hasattr(r, 'methods')])"
```

### Current Tech Stack
- Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), aiosqlite
- JWT (python-jose) + bcrypt (passlib) for auth
- Pydantic 2.0 for request/response validation

## Architecture Decisions
- Clean Architecture with 4 layers: entities, use_cases, interface_adapters, frameworks
- Each use case is a separate class with a single `execute()` method
- Gateway interfaces (ABCs) defined inside `use_cases/interfaces/` (not a separate layer)
- ORM models in frameworks/ (outermost) to keep inner layers framework-free
- Mapper functions in gateway repositories convert between ORM models and domain entities
- All table names: singular snake_case (user, post, comment, etc.)
- All datetime columns: timezone-aware with `DateTime(timezone=True)`
