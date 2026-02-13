# Instagram Clone - Modular Monolith

Vertical slicing by feature/domain. Each module is self-contained with its own models, services, schemas, and routes. Any module could theoretically be extracted into a microservice with minimal refactoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FastAPI App                               │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────┬──────┤
│ auth │ user │ post │ like │follow│ feed │story │ msg  │notif│search│
│      │      │      │      │      │      │      │      │     │      │
│routes│routes│routes│routes│routes│routes│routes│routes│route│routes│
│svc   │svc   │svc   │svc   │svc   │svc   │svc   │svc   │svc  │svc   │
│schema│schema│schema│schema│schema│schema│schema│schema│schma│schema│
│models│models│models│models│models│models│models│models│model│models│
├──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴─────┴──────┤
│                     Shared Infrastructure                           │
│              config / database / security / event_bus               │
└─────────────────────────────────────────────────────────────────────┘
```

Each module is a vertical slice containing all layers internally. Modules communicate through direct imports (replaceable with an event bus for looser coupling).

## Directory Structure

```
src/modular_monolith/
├── main.py
├── shared/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── base_model.py
│   └── event_bus.py
└── modules/
    ├── auth/           # User model, auth service, auth router
    ├── user/           # User profile service + router
    ├── post/           # Post + PostHashtag + Hashtag models
    ├── comment/        # Comment model, service, router
    ├── like/           # Like model, service, router
    ├── follow/         # Follow model, service, router
    ├── feed/           # Feed aggregation service + router
    ├── story/          # Story model, service, router
    ├── messaging/      # Message model, service, router
    ├── notification/   # Notification model, service, router
    └── search/         # Cross-module search service + router
```

Each module typically contains:

```
module/
├── __init__.py     # Public API (exports router)
├── models.py       # SQLAlchemy models
├── schemas.py      # Pydantic DTOs
├── service.py      # Business logic
└── router.py       # FastAPI endpoints
```

## Key Characteristics

- **Vertical slicing** by feature, not horizontal layers
- **Module ownership**: each module owns its data (models, schemas) and behavior (service, router)
- **Inter-module communication** through direct imports (could be replaced with event bus)
- **Minimal shared infrastructure**: only config, database, security, and event bus
- **Microservice-ready**: each of the 11 modules is a potential service boundary
- **11 modules total**: auth, user, post, comment, like, follow, feed, story, messaging, notification, search

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
cd 05-modular-monolith
uv sync
uv run uvicorn modular_monolith.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Tests

```bash
uv run pytest tests/ -v
```

30 tests covering all modules.

## API Endpoints

| Method | Path | Module | Description |
|--------|------|--------|-------------|
| POST | `/auth/register` | auth | Register new user |
| POST | `/auth/login` | auth | Login, receive JWT |
| GET | `/users/me` | user | Current user profile |
| GET | `/users/{id}` | user | Get user profile |
| PUT | `/users/me` | user | Update profile |
| POST | `/posts` | post | Create post |
| GET | `/posts/{id}` | post | Get post |
| GET | `/posts` | post | List posts |
| POST | `/posts/{id}/comments` | comment | Add comment |
| GET | `/posts/{id}/comments` | comment | List comments |
| POST | `/posts/{id}/like` | like | Like a post |
| DELETE | `/posts/{id}/like` | like | Unlike a post |
| POST | `/users/{id}/follow` | follow | Follow user |
| DELETE | `/users/{id}/follow` | follow | Unfollow user |
| GET | `/feed` | feed | Get personalized feed |
| POST | `/stories` | story | Create story |
| GET | `/stories` | story | Get stories feed |
| POST | `/messages` | messaging | Send message |
| GET | `/messages/{user_id}` | messaging | Get conversation |
| GET | `/notifications` | notification | Get notifications |
| GET | `/search` | search | Search users/posts/hashtags |
