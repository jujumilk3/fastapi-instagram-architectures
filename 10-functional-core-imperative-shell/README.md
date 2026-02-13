# Instagram Clone - Functional Core, Imperative Shell Architecture

Business logic lives in **pure functions** (no side effects, no DB, no IO). All IO (database, HTTP, JWT) is pushed to the **imperative shell** at the edges. This makes the core trivially testable without mocking.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                          │
│            (Routers + Schemas)                       │
├─────────────────────────────────────────────────────┤
│              Imperative Shell (IO)                    │
│                                                      │
│  handlers/           models.py     security.py       │
│  ├── auth_handler    (SQLAlchemy   (JWT tokens,      │
│  ├── post_handler     ORM models)   password hash)   │
│  ├── comment_handler                                 │
│  ├── like_handler    database.py                     │
│  ├── follow_handler  (async engine                   │
│  ├── feed_handler     + session)                     │
│  ├── story_handler                                   │
│  ├── message_handler                                 │
│  ├── notification_handler                            │
│  ├── search_handler                                  │
│  └── user_handler                                    │
├─────────────────────────────────────────────────────┤
│              Functional Core (Pure)                   │
│                                                      │
│  core/                                               │
│  ├── auth.py        validate_registration()          │
│  ├── post.py        extract_hashtags(), can_delete() │
│  ├── comment.py     validate_comment()               │
│  ├── like.py        toggle_like_result()             │
│  ├── follow.py      validate_follow()                │
│  ├── message.py     validate_message()               │
│  ├── notification.py build_notification()            │
│  ├── story.py       validate_story()                 │
│  ├── search.py      build_search_results()           │
│  └── types.py       Result type + domain types       │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/functional_core/
├── main.py
├── api/
│   ├── dependencies.py
│   ├── routers.py          # FastAPI route definitions
│   └── schemas.py          # Pydantic DTOs
├── core/                    # Pure functions (no IO)
│   ├── auth.py             # Registration/login validation
│   ├── post.py             # Hashtag extraction, ownership checks
│   ├── comment.py          # Comment validation
│   ├── like.py             # Like toggle logic
│   ├── follow.py           # Follow validation
│   ├── message.py          # Message validation
│   ├── notification.py     # Notification building
│   ├── story.py            # Story validation
│   ├── search.py           # Search result building
│   └── types.py            # Result type, domain types
└── shell/                   # IO and side effects
    ├── database.py         # Async engine + session
    ├── models.py           # SQLAlchemy ORM models
    ├── security.py         # JWT + password hashing
    └── handlers/           # Orchestrate core + IO
        ├── auth_handler.py
        ├── post_handler.py
        ├── comment_handler.py
        ├── like_handler.py
        ├── follow_handler.py
        ├── feed_handler.py
        ├── story_handler.py
        ├── message_handler.py
        ├── notification_handler.py
        ├── search_handler.py
        └── user_handler.py
```

## Key Characteristics

- **Pure core** - business logic functions have no side effects, no DB access, no IO
- **Testable without mocking** - core functions can be tested with plain values
- **IO at the edges** - shell handlers orchestrate: read DB → call pure function → write DB
- **Clear dependency direction** - API → Shell → Core (dependencies flow inward)
- **Result type** - core returns typed results instead of raising exceptions

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
cd 10-functional-core-imperative-shell
uv sync
uv run uvicorn functional_core.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Tests

```bash
uv run pytest tests/ -v
```

Includes both API integration tests and pure core unit tests (`tests/test_core.py`).

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
