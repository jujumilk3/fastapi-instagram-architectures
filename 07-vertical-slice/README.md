# Instagram Clone - Vertical Slice Architecture

Each feature is a self-contained vertical slice with its own Request, Handler, and Response. A mediator pattern routes requests to handlers, keeping slices completely independent of each other.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                          │
│            (Routers + Schemas)                       │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│  Auth    │  Post    │  Follow  │  Story   │  ...    │
│  Slice   │  Slice   │  Slice   │  Slice   │         │
│          │          │          │          │         │
│ Request  │ Request  │ Request  │ Request  │         │
│    ↓     │    ↓     │    ↓     │    ↓     │         │
│ Handler  │ Handler  │ Handler  │ Handler  │         │
│    ↓     │    ↓     │    ↓     │    ↓     │         │
│ Response │ Response │ Response │ Response │         │
├──────────┴──────────┴──────────┴──────────┴─────────┤
│              Mediator (Request Dispatcher)            │
├─────────────────────────────────────────────────────┤
│              Shared (DB, Security, Models)            │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/vertical_slice/
├── main.py
├── api/
│   ├── dependencies.py
│   ├── routers.py          # All FastAPI route definitions
│   └── schemas.py          # Pydantic request/response DTOs
├── features/
│   ├── auth/               # register, login, get_me
│   ├── post/               # create, delete, get
│   ├── comment/            # create, delete, get_comments
│   ├── like/               # toggle_like
│   ├── follow/             # follow_user, unfollow_user
│   ├── feed/               # get_feed
│   ├── story/              # create, delete, get_my, get_feed
│   ├── message/            # send, get_conversations, get_conversation, mark_read
│   ├── notification/       # get, mark_read, mark_all_read
│   ├── search/             # search_users, search_hashtags, get_posts_by_hashtag
│   └── user/               # get_profile, get_posts, get_followers, get_following, update
├── models/
│   ├── base.py             # DeclarativeBase + TimestampMixin
│   └── tables.py           # All SQLAlchemy ORM models
└── shared/
    ├── database.py         # Async engine + session
    ├── mediator.py         # Request → Handler dispatcher
    └── security.py         # JWT + password hashing
```

## Key Characteristics

- **Feature cohesion over technical layers** - each business capability is a complete vertical slice
- **Mediator pattern** - `mediator.register(RequestType, handler)` routes requests to isolated handlers
- **Request/Response dataclasses** - each operation defines explicit input/output contracts
- **No cross-slice dependencies** - slices share only infrastructure (DB, security)
- **Easy to extend** - add a new feature without touching existing slices

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
cd 07-vertical-slice
uv sync
uv run uvicorn vertical_slice.main:app --reload
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
