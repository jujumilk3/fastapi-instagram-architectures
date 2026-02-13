# Instagram Clone - Microkernel (Plugin) Architecture

A minimal core system provides infrastructure (database, auth, plugin registry). Each domain feature is a self-contained plugin that registers itself with the core via a `Plugin` ABC and `PluginRegistry`.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Plugin Registry                     │
│         (discovers, registers, starts plugins)       │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬────┤
│ Auth │ Post │ User │Follow│ Feed │Story │ Msg  │ ...│
│Plugin│Plugin│Plugin│Plugin│Plugin│Plugin│Plugin│    │
│      │      │      │      │      │      │      │    │
│router│router│router│router│router│router│router│    │
│service│service│service│service│service│service│service│    │
│models│models│      │models│      │models│models│    │
│schemas│schemas│schemas│      │      │schemas│schemas│    │
├──────┴──────┴──────┴──────┴──────┴──────┴──────┴────┤
│                    Core System                       │
│  ├── database.py    (async engine + session)         │
│  ├── security.py    (JWT + password hashing)         │
│  ├── plugin.py      (Plugin ABC)                     │
│  ├── registry.py    (PluginRegistry)                 │
│  └── base_model.py  (SQLAlchemy base)                │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/microkernel/
├── main.py
├── core/                    # Minimal core system
│   ├── base_model.py        # DeclarativeBase
│   ├── database.py          # Async engine + session factory
│   ├── plugin.py            # Plugin abstract base class
│   ├── registry.py          # Plugin lifecycle management
│   ├── schemas.py           # Shared Pydantic DTOs
│   └── security.py          # JWT + password hashing
└── plugins/                 # Feature plugins
    ├── __init__.py          # PLUGIN_LIST (all registered plugins)
    ├── auth/
    │   ├── plugin.py        # AuthPlugin(Plugin)
    │   ├── router.py        # FastAPI routes
    │   ├── service.py       # Business logic
    │   ├── models.py        # SQLAlchemy models
    │   └── schemas.py       # Pydantic DTOs
    ├── post/
    ├── user/
    ├── follow/
    ├── feed/
    ├── story/
    ├── message/
    ├── notification/
    └── search/
```

## Key Characteristics

- **Plugin ABC** - each feature implements `name` property and `register(app)` method
- **PluginRegistry** - manages plugin lifecycle, auto-registers routers at startup
- **Self-contained plugins** - each has its own router, service, models, and schemas
- **Enable/disable features** - add or remove plugins from `PLUGIN_LIST` without touching core
- **Minimal core** - only database, security, and plugin infrastructure in the core

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
cd 09-microkernel
uv sync
uv run uvicorn microkernel.main:app --reload
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
