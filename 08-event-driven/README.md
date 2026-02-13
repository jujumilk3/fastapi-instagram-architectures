# Instagram Clone - Event-Driven Architecture

All inter-component communication happens through events. Components are decoupled producers and consumers connected via an in-memory event broker. The system reacts to domain events rather than direct method calls.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                          │
│            (Routers + Schemas)                       │
├──────────────────┬──────────────────────────────────┤
│    Producers     │           Queries                 │
│  (Write Ops)     │         (Read Ops)                │
│                  │                                   │
│  auth_producer   │   feed_queries                    │
│  post_producer   │   post_queries                    │
│  comment_producer│   user_queries                    │
│  like_producer   │   message_queries                 │
│  follow_producer │   notification_queries            │
│  story_producer  │   search_queries                  │
│  message_producer│   story_queries                   │
├──────────────────┴──────────────────────────────────┤
│              Event Broker (Pub/Sub)                   │
│   POST_CREATED ─→ hashtag_consumer                   │
│   POST_LIKED   ─→ notification_consumer              │
│   USER_FOLLOWED─→ notification_consumer              │
│   COMMENT_ADDED─→ notification_consumer              │
├─────────────────────────────────────────────────────┤
│    Consumers (Side Effects)                          │
│    ├── hashtag_consumer     (extract & index tags)   │
│    └── notification_consumer (create notifications)  │
├─────────────────────────────────────────────────────┤
│              Shared (DB, Security, Models)            │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/event_driven/
├── main.py
├── api/
│   ├── dependencies.py
│   ├── routers.py          # FastAPI route definitions
│   └── schemas.py          # Pydantic DTOs
├── events/
│   └── definitions.py      # Event type constants (17 events)
├── producers/              # Write operations + event publishing
│   ├── auth_producer.py
│   ├── post_producer.py
│   ├── comment_producer.py
│   ├── like_producer.py
│   ├── follow_producer.py
│   ├── story_producer.py
│   └── message_producer.py
├── consumers/              # Event handlers (side effects)
│   ├── hashtag_consumer.py
│   └── notification_consumer.py
├── queries/                # Read-only data access
│   ├── feed_queries.py
│   ├── post_queries.py
│   ├── user_queries.py
│   ├── message_queries.py
│   ├── notification_queries.py
│   ├── search_queries.py
│   └── story_queries.py
├── models/
│   ├── base.py
│   └── tables.py
└── shared/
    ├── database.py
    ├── event_broker.py     # In-memory pub/sub broker
    └── security.py
```

## Key Characteristics

- **Event-driven decoupling** - producers publish events, consumers react to them independently
- **CQRS-like separation** - write operations (producers) and read operations (queries) are distinct
- **Side effects via consumers** - notifications, hashtag extraction handled asynchronously through event handlers
- **17 domain events** - `post.created`, `post.liked`, `user.followed`, `comment.added`, etc.
- **Easy to add behavior** - new consumers can subscribe to existing events without modifying producers

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- aiosqlite
- Pydantic v2
- JWT authentication (python-jose)
- Password hashing (passlib + bcrypt)

## Quick Start

```bash
cd 08-event-driven
uv sync
uv run uvicorn event_driven.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Tests

```bash
uv run pytest tests/ -v
```

37 tests covering all domains plus event broker unit tests.

## API Endpoints

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and receive JWT token |
| GET | `/api/auth/me` | Get current user profile |

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/users/{user_id}` | Get user profile |
| PUT | `/api/users/me` | Update current user profile |
| GET | `/api/users/{user_id}/posts` | Get user's posts |
| GET | `/api/users/{user_id}/followers` | List followers |
| GET | `/api/users/{user_id}/following` | List following |

### Posts

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/posts` | Create a new post |
| GET | `/api/posts/{post_id}` | Get post by ID |
| DELETE | `/api/posts/{post_id}` | Delete a post |
| POST | `/api/posts/{post_id}/likes` | Toggle like on post |
| GET | `/api/posts/{post_id}/comments` | List comments on post |
| POST | `/api/posts/{post_id}/comments` | Add comment to post |
| DELETE | `/api/posts/comments/{comment_id}` | Delete a comment |

### Follows

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/follow/{following_id}` | Follow a user |
| DELETE | `/api/follow/{following_id}` | Unfollow a user |

### Feed

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/feed` | Get user's feed |

### Stories

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/stories` | Create a story |
| GET | `/api/stories` | List my stories |
| GET | `/api/stories/feed` | Get story feed |
| DELETE | `/api/stories/{story_id}` | Delete a story |

### Messages

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/messages` | Send a direct message |
| GET | `/api/messages` | List conversations |
| GET | `/api/messages/{other_user_id}` | Get conversation with user |
| POST | `/api/messages/{sender_id}/read` | Mark messages as read |

### Notifications

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/notifications` | List notifications |
| POST | `/api/notifications/{notification_id}/read` | Mark notification as read |
| POST | `/api/notifications/read-all` | Mark all notifications as read |

### Search

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/search/users` | Search users |
| GET | `/api/search/hashtags` | Search hashtags |
| GET | `/api/search/posts/hashtag/{tag}` | Get posts by hashtag |
