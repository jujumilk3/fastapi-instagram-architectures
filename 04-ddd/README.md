# Instagram Clone - Domain-Driven Design

Rich domain model with Aggregates, Value Objects, and Domain Events. Business logic lives inside domain entities, not services. The domain layer is the core -- it has no dependencies on frameworks or infrastructure.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Infrastructure Layer                                   │
│  ORM, API Routers, Security, Repositories (concrete)    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Application Layer                              │    │
│  │  Services (orchestration, no business logic)    │    │
│  │                                                 │    │
│  │  ┌─────────────────────────────────────────┐    │    │
│  │  │  Domain Layer (core)                    │    │    │
│  │  │  Aggregates, Entities, Value Objects,   │    │    │
│  │  │  Domain Events, Repository ABCs         │    │    │
│  │  └─────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘

Dependencies flow inward: Infrastructure → Application → Domain
```

## Directory Structure

```
src/ddd/
├── main.py
├── domain/
│   ├── shared/
│   │   ├── entity.py              # Base Entity, AggregateRoot
│   │   ├── value_object.py        # Base ValueObject
│   │   └── event.py               # UserRegistered, PostCreated, PostLiked, etc.
│   ├── user/
│   │   ├── aggregate.py           # UserAggregate (create, update_profile, collect_events)
│   │   ├── value_objects.py       # Email, Username (frozen, validated)
│   │   └── repository.py          # UserRepository ABC
│   ├── post/
│   │   ├── aggregate.py           # PostAggregate (add_comment, toggle_like, extract_hashtags)
│   │   ├── entities.py            # Comment, Like child entities
│   │   └── repository.py
│   ├── social/
│   ├── messaging/
│   ├── notification/
│   └── hashtag/
├── application/                   # One service per bounded context
│   ├── auth/service.py
│   ├── user/service.py
│   ├── post/service.py            # Post, Comment, Like operations
│   ├── social/service.py          # Follow, Story operations
│   ├── feed/service.py
│   ├── messaging/service.py
│   ├── notification/service.py
│   └── search/service.py
└── infrastructure/
    ├── database.py
    ├── security.py
    ├── orm/
    │   ├── models.py              # SQLAlchemy ORM models
    │   └── mapper.py              # Domain ↔ ORM mapping
    ├── repositories/              # Concrete SQLAlchemy repositories
    └── api/
        ├── schemas.py
        ├── routers.py
        └── dependencies.py
```

## Key Characteristics

### Rich Domain Model

Aggregates contain behavior, not just data:

- `UserAggregate.update_profile()` -- validates and applies profile changes
- `PostAggregate.add_comment()` -- adds comment and raises `CommentAdded` event
- `PostAggregate.toggle_like()` -- manages like/unlike and raises `PostLiked` event
- `PostAggregate.extract_hashtags()` -- parses hashtags from post caption

### Value Objects

Immutable, self-validating types that represent domain concepts:

- `Email` -- frozen dataclass, validates format on creation
- `Username` -- frozen dataclass, validates length and allowed characters

### Domain Events

Events raised by aggregates to signal state changes:

- `UserRegistered` -- new user signed up
- `PostCreated` -- new post published
- `PostLiked` -- user liked a post
- `CommentAdded` -- comment added to a post

Events are collected within aggregates and dispatched after persistence.

### Aggregate Root Pattern

Child entities (Comment, Like) are only accessed through their parent aggregate's methods. External code never modifies children directly -- all mutations go through the aggregate root.

### Repository Pattern

- **Interfaces** defined in `domain/` (each bounded context owns its contract)
- **Implementations** in `infrastructure/repositories/` (SQLAlchemy)
- Explicit **mapper layer** (`infrastructure/orm/mapper.py`) keeps domain objects free from ORM annotations

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Web Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | aiosqlite |
| Validation | Pydantic v2 |
| Auth | JWT + bcrypt |

## Quick Start

```bash
cd 04-ddd
uv sync
uv run uvicorn ddd.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Tests

```bash
uv run pytest tests/ -v
```

29 tests covering aggregates, services, and API endpoints.

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Current user profile |

### Users
| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/{username}` | Get user profile |
| PUT | `/users/me` | Update profile |
| GET | `/users/{username}/followers` | List followers |
| GET | `/users/{username}/following` | List following |

### Posts
| Method | Path | Description |
|--------|------|-------------|
| POST | `/posts` | Create post |
| GET | `/posts/{id}` | Get post |
| GET | `/users/{username}/posts` | Get user posts |
| DELETE | `/posts/{id}` | Delete post |

### Comments
| Method | Path | Description |
|--------|------|-------------|
| POST | `/posts/{id}/comments` | Add comment |
| GET | `/posts/{id}/comments` | List comments |
| DELETE | `/comments/{id}` | Delete comment |

### Likes
| Method | Path | Description |
|--------|------|-------------|
| POST | `/posts/{id}/like` | Toggle like |

### Follow
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/{username}/follow` | Follow user |
| DELETE | `/users/{username}/follow` | Unfollow user |

### Feed
| Method | Path | Description |
|--------|------|-------------|
| GET | `/feed` | Get feed from followed users |

### Stories
| Method | Path | Description |
|--------|------|-------------|
| POST | `/stories` | Create story |
| GET | `/stories/me` | Get my stories |
| GET | `/stories/feed` | Get story feed |
| DELETE | `/stories/{id}` | Delete story |

### Messages
| Method | Path | Description |
|--------|------|-------------|
| POST | `/messages` | Send message |
| GET | `/messages/conversations` | List conversations |
| GET | `/messages/conversations/{user_id}` | Get conversation |
| PUT | `/messages/conversations/{user_id}/read` | Mark as read |

### Notifications
| Method | Path | Description |
|--------|------|-------------|
| GET | `/notifications` | List notifications |
| PUT | `/notifications/{id}/read` | Mark as read |
| PUT | `/notifications/read-all` | Mark all as read |

### Search
| Method | Path | Description |
|--------|------|-------------|
| GET | `/search/users` | Search users |
| GET | `/search/hashtags` | Search hashtags |
| GET | `/search/hashtags/{tag}/posts` | Get posts by hashtag |
