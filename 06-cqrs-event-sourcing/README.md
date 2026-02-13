# Instagram Clone - CQRS + Event Sourcing

Strict separation of write (commands) and read (queries) paths. All state changes are stored as immutable events in an append-only event store. Read models are denormalized projections rebuilt from events.

## Architecture

```
                         ┌─────────────┐
                         │   FastAPI    │
                         │     API      │
                         └──────┬───────┘
                    ┌───────────┴───────────┐
                    ▼                       ▼
             Write Path                Read Path
                    │                       │
                    ▼                       ▼
              ┌──────────┐           ┌──────────┐
              │ Command  │           │  Query   │
              └────┬─────┘           └────┬─────┘
                   ▼                      ▼
              ┌──────────┐           ┌──────────┐
              │ Command  │           │  Query   │
              │   Bus    │           │   Bus    │
              └────┬─────┘           └────┬─────┘
                   ▼                      ▼
              ┌──────────┐           ┌──────────┐
              │ Command  │           │  Query   │
              │ Handler  │           │ Handler  │
              └────┬─────┘           └────┬─────┘
                   ▼                      ▼
              ┌──────────┐           ┌──────────┐
              │Aggregate │           │Projection│
              └────┬─────┘           │(read mdl)│
                   ▼                 └──────────┘
              ┌──────────┐                ▲
              │  Event   │                │
              │  Store   │                │
              └────┬─────┘                │
                   ▼                      │
              ┌──────────┐           ┌──────────┐
              │  Event   │──────────▶│Projection│
              │   Bus    │           │ Handler  │
              └──────────┘           └──────────┘
```

**Write path**: API receives a command, dispatches it through the command bus to a handler, which validates via the aggregate and appends events to the event store. The event bus then notifies projection handlers.

**Read path**: API receives a query, dispatches it through the query bus to a handler, which reads directly from denormalized projection tables.

## Directory Structure

```
src/cqrs_es/
├── main.py
├── shared/
│   ├── database.py       # SQLAlchemy engine + Base
│   ├── security.py       # JWT + bcrypt
│   ├── event_store.py    # Append-only event store
│   ├── command_bus.py    # Command dispatch
│   ├── query_bus.py      # Query dispatch
│   └── event_bus.py      # Event pub/sub
├── write/
│   ├── commands/
│   │   └── commands.py   # 16 command dataclasses
│   ├── events/
│   │   └── events.py     # Event type constants
│   ├── aggregates/
│   │   ├── user.py       # UserAggregate
│   │   ├── post.py       # PostAggregate
│   │   └── social.py     # Follow, Story, Message, Notification aggregates
│   └── handlers/
│       ├── auth.py       # Register, login, update user
│       ├── post.py       # Post, like, comment handlers
│       ├── social.py     # Follow, story handlers
│       └── messaging.py  # Message, notification handlers
├── read/
│   ├── projections/
│   │   ├── models.py     # 10 denormalized projection tables
│   │   └── handlers.py   # 16 event handlers updating projections
│   ├── queries/
│   │   └── queries.py    # 17 query dataclasses
│   └── handlers/
│       └── handlers.py   # 17 query handlers
└── api/
    ├── schemas.py
    ├── routers.py
    └── dependencies.py
```

## Key Characteristics

- **CQRS**: write and read paths are completely separate -- different models, different handlers, different data stores
- **Event Sourcing**: the event_store table is the source of truth; all state is derived from the append-only event stream
- **Projections**: denormalized read models updated asynchronously by event handlers for fast query performance
- **In-memory buses**: dict-based command/query/event dispatch (no external message broker required)
- **16 commands**: RegisterUser, LoginUser, CreatePost, LikePost, AddComment, FollowUser, etc.
- **16 event types**: USER_REGISTERED, POST_CREATED, POST_LIKED, COMMENT_ADDED, USER_FOLLOWED, etc.
- **17 queries**: GetUserProfile, GetPost, GetFeed, GetComments, GetFollowers, SearchUsers, etc.
- **All handlers registered at app startup** in the FastAPI lifespan context

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- aiosqlite
- Pydantic v2
- JWT (python-jose)
- bcrypt (passlib)

## Quick Start

```bash
cd 06-cqrs-event-sourcing
uv sync
uv run uvicorn cqrs_es.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Tests

```bash
uv run pytest tests/ -v
```

29 tests covering commands, queries, projections, and API endpoints.

## API Endpoints

| Method | Path | Type | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | Command | Register new user |
| POST | `/auth/login` | Command | Login, receive JWT |
| GET | `/users/me` | Query | Current user profile |
| GET | `/users/{id}` | Query | Get user profile |
| PUT | `/users/me` | Command | Update profile |
| POST | `/posts` | Command | Create post |
| GET | `/posts/{id}` | Query | Get post |
| GET | `/posts` | Query | List posts |
| POST | `/posts/{id}/comments` | Command | Add comment |
| GET | `/posts/{id}/comments` | Query | List comments |
| POST | `/posts/{id}/like` | Command | Like a post |
| DELETE | `/posts/{id}/like` | Command | Unlike a post |
| POST | `/users/{id}/follow` | Command | Follow user |
| DELETE | `/users/{id}/follow` | Command | Unfollow user |
| GET | `/feed` | Query | Get personalized feed |
| POST | `/stories` | Command | Create story |
| GET | `/stories` | Query | Get stories feed |
| POST | `/messages` | Command | Send message |
| GET | `/messages/{user_id}` | Query | Get conversation |
| GET | `/notifications` | Query | Get notifications |
| GET | `/search` | Query | Search users/posts/hashtags |

Every POST/PUT/DELETE endpoint dispatches a command through the command bus, which produces events stored in the event store. Every GET endpoint dispatches a query that reads from projection tables.
