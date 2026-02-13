# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Full CQRS + Event Sourcing Architecture Implemented
- ✅ Event store (append-only table storing all events as JSON)
- ✅ Command bus, query bus, event bus (in-memory dict-based dispatch)
- ✅ Write side: commands, events, aggregates, command handlers
- ✅ Read side: projection models (denormalized), projection event handlers, query handlers
- ✅ API layer: schemas, routers, dependencies (JWT + bcrypt auth)
- ✅ All 36 endpoints matching spec (auth, users, posts, follow, feed, stories, messages, notifications, search)
- ✅ Hashtag extraction from post content
- ✅ Notification generation on like, comment, follow
- ✅ `uv sync` and route verification passing

## Code Location Map

### Shared (`src/cqrs_es/shared/`)
- `database.py` - SQLAlchemy async engine, session factory, Base
- `security.py` - JWT token + bcrypt password hashing
- `event_store.py` - EventStoreModel, append_event(), load_events()
- `command_bus.py` - register_command_handler(), dispatch_command()
- `query_bus.py` - register_query_handler(), dispatch_query()
- `event_bus.py` - subscribe(), publish()

### Write Side (`src/cqrs_es/write/`)
- `commands/commands.py` - 16 command dataclasses
- `events/events.py` - Event type constants
- `aggregates/user.py` - UserAggregate (register, update)
- `aggregates/post.py` - PostAggregate (create, delete, like, comment)
- `aggregates/social.py` - FollowAggregate, StoryAggregate, MessageAggregate, NotificationAggregate
- `handlers/auth.py` - register, login, update user
- `handlers/post.py` - create/delete post, toggle like, create/delete comment
- `handlers/social.py` - follow/unfollow, create/delete story
- `handlers/messaging.py` - send message, mark read, notifications

### Read Side (`src/cqrs_es/read/`)
- `projections/models.py` - 10 projection models (denormalized read tables)
- `projections/handlers.py` - 16 event handlers that update projections
- `queries/queries.py` - 17 query dataclasses
- `handlers/handlers.py` - 17 query handlers reading from projections

### API (`src/cqrs_es/api/`)
- `schemas.py` - Pydantic DTOs
- `routers.py` - All FastAPI routes (36 endpoints)
- `dependencies.py` - OAuth2, get_current_user_id, get_session

### App Entry (`src/cqrs_es/main.py`)
- Wires command/query/event handlers on startup
- Creates all tables (event_store + projections)

## How to Work on This

### Setup
```bash
cd 06-cqrs-event-sourcing
uv sync
```

### Run
```bash
uv run uvicorn cqrs_es.main:app --reload
```

### Verify
```bash
uv run python -c "from cqrs_es.main import app; print('OK')"
```

### Current Tech Stack
- Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), aiosqlite
- JWT auth (python-jose), bcrypt (passlib)
- In-memory command/query/event buses
- SQLite event store + projection tables

## Architecture Decisions

- CQRS: Write side produces events via aggregates; read side uses denormalized projections
- Event Sourcing: All state changes stored as events in append-only event_store table
- Projections updated synchronously in same transaction for SQLite consistency
- Simple dict-based buses (no external message broker needed for this scale)
- ID generation via max(id)+1 on projection tables (sufficient for SQLite single-writer)
- Singular snake_case table names (my-dev-standards)
- All datetime fields timezone-aware (UTC)
