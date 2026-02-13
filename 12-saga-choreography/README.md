# Instagram Clone - Saga Choreography Architecture

Multi-step operations are managed by Sagas with automatic compensation (rollback) on failure. Asynchronous side effects (notifications, hashtag indexing) propagate through event choreography via an EventBus.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                          │
│            (Routers + Schemas)                       │
├─────────────────────────────────────────────────────┤
│                    Sagas                             │
│  (multi-step orchestration with compensation)        │
│                                                      │
│  create_post_saga   ──→ create post → extract tags   │
│  delete_post_saga   ──→ validate → delete            │
│  like_post_saga     ──→ toggle like → update count   │
│  comment_saga       ──→ create comment → update count│
│  follow_user_saga   ──→ create follow → notify       │
│  send_message_saga  ──→ create message → notify      │
│  create_story_saga  ──→ create story → update meta   │
├─────────────────────────────────────────────────────┤
│           Choreography (Event Handlers)              │
│                                                      │
│  EventBus ──→ on_post_created  (extract hashtags)    │
│           ──→ on_post_liked    (create notification)  │
│           ──→ on_comment_added (create notification)  │
│           ──→ on_user_followed (create notification)  │
├─────────────────────────────────────────────────────┤
│                   Services                           │
│  auth, post, comment, like, follow, message,         │
│  notification, story, feed, hashtag, search, user    │
├─────────────────────────────────────────────────────┤
│              Shared (DB, Security, EventBus, Saga)    │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/saga_choreography/
├── main.py
├── api/
│   ├── dependencies.py
│   ├── routers.py          # FastAPI route definitions
│   └── schemas.py          # Pydantic DTOs
├── sagas/                   # Multi-step orchestrations
│   ├── create_post_saga.py
│   ├── delete_post_saga.py
│   ├── like_post_saga.py
│   ├── comment_saga.py
│   ├── follow_user_saga.py
│   ├── send_message_saga.py
│   └── create_story_saga.py
├── choreography/
│   └── handlers.py          # Event reaction handlers
├── events/
│   └── definitions.py       # Event type constants
├── services/                # Domain services
│   ├── auth_service.py
│   ├── post_service.py
│   ├── comment_service.py
│   ├── like_service.py
│   ├── follow_service.py
│   ├── message_service.py
│   ├── notification_service.py
│   ├── story_service.py
│   ├── feed_service.py
│   ├── hashtag_service.py
│   ├── search_service.py
│   └── user_service.py
├── models/
│   ├── base.py
│   └── tables.py            # Includes SagaLog table
└── shared/
    ├── database.py
    ├── event_bus.py          # In-memory pub/sub
    ├── saga.py               # SagaExecutor + SagaStep
    └── security.py
```

## Key Characteristics

- **Saga pattern** - multi-step operations with automatic compensation on failure
- **SagaLog table** - audit trail tracking step execution (started, completed, compensating, compensated)
- **Event choreography** - side effects (notifications, hashtag indexing) triggered by domain events
- **Mixed consistency** - sagas provide strong consistency for critical paths, events provide eventual consistency for side effects
- **12 domain services** - each service encapsulates domain logic and database operations

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
cd 12-saga-choreography
uv sync
uv run uvicorn saga_choreography.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Tests

```bash
uv run pytest tests/ -v
```

39 tests covering all domains plus saga infrastructure tests (compensation, event bus).

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
| POST | `/api/posts` | Create a new post (saga) |
| GET | `/api/posts/{post_id}` | Get post by ID |
| DELETE | `/api/posts/{post_id}` | Delete a post (saga) |
| POST | `/api/posts/{post_id}/likes` | Toggle like (saga) |
| GET | `/api/posts/{post_id}/comments` | List comments on post |
| POST | `/api/posts/{post_id}/comments` | Add comment (saga) |
| DELETE | `/api/posts/comments/{comment_id}` | Delete a comment |

### Follows

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/follow/{following_id}` | Follow a user (saga) |
| DELETE | `/api/follow/{following_id}` | Unfollow a user |

### Feed

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/feed` | Get user's feed |

### Stories

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/stories` | Create a story (saga) |
| GET | `/api/stories` | List my stories |
| GET | `/api/stories/feed` | Get story feed |
| DELETE | `/api/stories/{story_id}` | Delete a story |

### Messages

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/messages` | Send a direct message (saga) |
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
