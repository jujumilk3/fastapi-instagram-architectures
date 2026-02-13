# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Full Actor Model Architecture Implemented
- ✅ Actor base class with asyncio.Queue mailbox and Ask/Reply pattern in `src/actor_model/actors/base.py`
- ✅ ActorRegistry for named actor lookup and message routing in `src/actor_model/actors/registry.py`
- ✅ 10 domain actors: User, Post, Comment, Like, Follow, Feed, Story, Message, Notification, Search
- ✅ Cross-actor notifications (Like, Comment, Follow actors create Notification records)
- ✅ Thin API routers that create messages, send to actors, and await responses
- ✅ All 29 API tests passing
- ✅ Session-scoped async test setup with actors running as background tasks

## Code Location Map

### Actor Framework (`src/actor_model/actors/`)
- `base.py` - Actor ABC with mailbox, Ask pattern (Message with Future for request-response)
- `registry.py` - ActorRegistry: register, get, send, start_all, stop_all
- `messages.py` - All message dataclasses (RegisterMessage, LoginMessage, CreatePostMessage, etc.)

### Domain Actors (`src/actor_model/actors/`)
- `user_actor.py` - Register, Login, GetProfile, UpdateProfile, GetFollowers, GetFollowing
- `post_actor.py` - CreatePost, GetPost, DeletePost, GetUserPosts + hashtag extraction
- `comment_actor.py` - CreateComment, GetComments, DeleteComment + notification on create
- `like_actor.py` - ToggleLike + notification on like
- `follow_actor.py` - FollowUser, UnfollowUser + notification on follow
- `feed_actor.py` - GetFeed (follows + own posts)
- `story_actor.py` - CreateStory, GetStories, GetStoryFeed, DeleteStory (24h TTL)
- `message_actor.py` - SendMessage, GetConversations, GetConversation, MarkRead
- `notification_actor.py` - GetNotifications, MarkRead, MarkAllRead
- `search_actor.py` - SearchUsers, SearchHashtags, GetPostsByHashtag

### Shared (`src/actor_model/shared/`)
- `database.py` - async SQLAlchemy engine, sessionmaker, get_db
- `security.py` - JWT (python-jose) + bcrypt password hashing

### Models (`src/actor_model/models/`)
- `base.py` - DeclarativeBase + TimestampMixin (timezone-aware)
- `tables.py` - All ORM models (User, Post, Comment, Like, Follow, Hashtag, PostHashtag, Story, Message, Notification)

### API (`src/actor_model/api/`)
- `schemas.py` - Pydantic v2 request/response DTOs
- `dependencies.py` - get_current_user_id (JWT), get_registry (from app.state)
- `routers.py` - Thin routers: create message -> send to actor -> await response

### Application
- `main.py` - FastAPI app, lifespan (create tables, start/stop actors), create_registry()

### Tests
- `tests/conftest.py` - Session-scoped DB + registry setup, test client fixtures
- `tests/test_api.py` - 29 integration tests covering all endpoints

## How to Work on This

### Setup
```bash
cd 11-actor-model
uv sync
```

### Run Server
```bash
uv run fastapi dev src/actor_model/main.py
```

### Run Tests
```bash
uv run pytest tests/ -v
```

### Current Tech Stack
- Python 3.11+, FastAPI, SQLAlchemy 2.0 async, aiosqlite
- Pydantic v2, python-jose (JWT), passlib[bcrypt]
- asyncio.Queue for actor mailboxes
- uv package manager, hatchling build

## Architecture Decisions
- Each actor processes messages ONE AT A TIME via asyncio.Queue (sequential within actor, concurrent between actors)
- Ask pattern: messages carry an asyncio.Future for request-response
- DB session created per message (actors hold a session factory reference via registry._db_factory)
- Notifications created inline within Like/Comment/Follow actors rather than via cross-actor message passing (simpler, same DB transaction)
- Actor _run loop uses wait_for with 0.5s timeout to allow clean shutdown
