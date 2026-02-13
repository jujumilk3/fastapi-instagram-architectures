# Project Status

**Last Updated:** 2026-02-13 15:00 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Event-Driven Architecture Fully Implemented
- ✅ Complete event-driven architecture with in-memory pub/sub broker
- ✅ 7 producers: auth, post, comment, like, follow, story, message
- ✅ 2 consumers: notification (like/comment/follow), hashtag extraction
- ✅ 7 query modules: user, post, feed, story, message, notification, search
- ✅ Full REST API with 28 endpoints matching project spec
- ✅ 37 tests passing (6 auth, 3 user, 4 post, 2 comment, 1 like, 3 follow, 1 feed, 3 story, 2 message, 5 notification, 3 search, 4 event broker)
- ✅ Event-driven side effects: notifications auto-created on like/comment/follow
- ✅ Hashtags auto-extracted from post content on PostCreated event

## Next Actions (Priority Order)

1. **[LOW]** Add more edge case tests (duplicate follow, self-like notifications)
2. **[LOW]** Add pagination tests for feed/posts/messages

## Code Location Map

### Shared (`src/event_driven/shared/`)
- `database.py` - Async SQLAlchemy engine, session factory, get_db
- `security.py` - JWT token creation/decode, bcrypt password hashing
- `event_broker.py` - In-memory EventBroker with subscribe/publish/clear

### Models (`src/event_driven/models/`)
- `base.py` - TimestampMixin with timezone-aware created_at
- `tables.py` - All ORM models: User, Post, Comment, Like, Follow, Story, Message, Notification, Hashtag, PostHashtag

### Events (`src/event_driven/events/`)
- `definitions.py` - Event type constants (e.g. "post.liked", "user.followed")

### Producers (`src/event_driven/producers/`)
- `auth_producer.py` - register_user, login_user, update_user
- `post_producer.py` - create_post, delete_post
- `comment_producer.py` - create_comment, delete_comment
- `like_producer.py` - toggle_like
- `follow_producer.py` - follow_user, unfollow_user
- `story_producer.py` - create_story, delete_story
- `message_producer.py` - send_message, mark_messages_read, mark_notification_read, mark_all_notifications_read

### Consumers (`src/event_driven/consumers/`)
- `notification_consumer.py` - on_post_liked, on_comment_added, on_user_followed
- `hashtag_consumer.py` - on_post_created (extracts #hashtags)

### Queries (`src/event_driven/queries/`)
- `user_queries.py` - get_user_by_id, get_user_by_email, get_user_profile
- `post_queries.py` - get_post, get_user_posts, get_post_comments
- `feed_queries.py` - get_feed
- `story_queries.py` - get_my_stories, get_story_feed
- `message_queries.py` - get_conversations, get_conversation
- `notification_queries.py` - get_notifications
- `search_queries.py` - search_users, search_hashtags, get_posts_by_hashtag

### API (`src/event_driven/api/`)
- `schemas.py` - Pydantic request/response models
- `dependencies.py` - get_current_user_id, get_session
- `routers.py` - All FastAPI routers (auth, user, post, follow, feed, story, message, notification, search)

### App Entry (`src/event_driven/main.py`)
- Lifespan wires consumers to broker, creates tables
- FastAPI app with all routers

### Tests (`tests/`)
- `conftest.py` - Test DB setup, client/auth fixtures
- `test_api.py` - 37 tests across 11 test classes

## How to Work on This

### Setup
```bash
cd 08-event-driven
uv sync
```

### Run Server
```bash
uv run uvicorn event_driven.main:app --reload
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

- **In-memory event broker** instead of external message queue (Redis/RabbitMQ) for simplicity
- **DB is source of truth**, events are for side effects only (not event sourcing)
- **Consumers receive db session** via event_data dict to write in the same transaction
- **Singular snake_case** table names per project conventions
- **Timezone-aware DateTime** columns with UTC default
