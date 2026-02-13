# Instagram Clone - Actor Model Architecture

Each domain concept is an independent Actor with private state, processing messages one at a time through an `asyncio.Queue` mailbox. Actors communicate via addressed messages (not broadcast), providing built-in concurrency safety.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                          │
│            (Routers + Schemas)                       │
├─────────────────────────────────────────────────────┤
│                Actor Registry                        │
│         (lifecycle, discovery, routing)               │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬────┤
│ User │ Post │Commt │ Like │Follow│ Feed │Story │ ...│
│Actor │Actor │Actor │Actor │Actor │Actor │Actor │    │
│      │      │      │      │      │      │      │    │
│ ┌──┐ │ ┌──┐ │ ┌──┐ │ ┌──┐ │ ┌──┐ │ ┌──┐ │ ┌──┐ │    │
│ │Q │ │ │Q │ │ │Q │ │ │Q │ │ │Q │ │ │Q │ │ │Q │ │    │
│ └──┘ │ └──┘ │ └──┘ │ └──┘ │ └──┘ │ └──┘ │ └──┘ │    │
│  ↓   │  ↓   │  ↓   │  ↓   │  ↓   │  ↓   │  ↓   │    │
│handle│handle│handle│handle│handle│handle│handle│    │
├──────┴──────┴──────┴──────┴──────┴──────┴──────┴────┤
│              Shared (DB, Security, Models)            │
└─────────────────────────────────────────────────────┘
         Q = asyncio.Queue mailbox (sequential processing)
```

## Directory Structure

```
src/actor_model/
├── main.py
├── actors/
│   ├── base.py              # Actor base class (queue + message loop)
│   ├── messages.py          # Message types (Message, Ask)
│   ├── registry.py          # Actor lifecycle management
│   ├── user_actor.py        # Registration, login, profile
│   ├── post_actor.py        # Create, delete, get posts + hashtags
│   ├── comment_actor.py     # Comment CRUD
│   ├── like_actor.py        # Like toggle
│   ├── follow_actor.py      # Follow/unfollow + notifications
│   ├── feed_actor.py        # Feed generation
│   ├── story_actor.py       # Story CRUD
│   ├── message_actor.py     # Direct messaging
│   ├── notification_actor.py # Notification management
│   └── search_actor.py      # User/hashtag search
├── api/
│   ├── dependencies.py
│   ├── routers.py           # FastAPI routes → actor messages
│   └── schemas.py           # Pydantic DTOs
├── models/
│   ├── base.py
│   └── tables.py            # SQLAlchemy ORM models
└── shared/
    ├── database.py
    └── security.py
```

## Key Characteristics

- **Message-based communication** - actors receive typed messages via `asyncio.Queue` mailboxes
- **Sequential processing** - each actor processes one message at a time (concurrency safety)
- **Ask pattern** - request-reply via `asyncio.Future` embedded in `Ask` messages
- **Actor registry** - centralized lifecycle management (start/stop all actors)
- **10 domain actors** - User, Post, Comment, Like, Follow, Feed, Story, Message, Notification, Search

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
cd 11-actor-model
uv sync
uv run uvicorn actor_model.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Tests

```bash
uv run pytest tests/ -v
```

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
