# Instagram Clone - Hexagonal Architecture (Ports & Adapters)

Dependencies always point inward toward the domain. External concerns (database, HTTP, security) are adapters that implement port interfaces, making the domain completely independent of infrastructure.

## Architecture

```
┌──────────────────────────────────────────────────┐
│                   Adapters                        │
│  ┌──────────────┐            ┌────────────────┐  │
│  │   Inbound     │            │    Outbound     │  │
│  │  (API/HTTP)   │            │  (DB/Security)  │  │
│  └──────┬───────┘            └───────▲────────┘  │
│         │    ┌──────────────────┐    │           │
│         │    │      Ports       │    │           │
│         │    │  ┌────────────┐  │    │           │
│         ├───►│  │  Inbound   │  │    │           │
│         │    │  │ (Use Cases)│  │    │           │
│         │    │  └────────────┘  │    │           │
│         │    │  ┌────────────┐  │    │           │
│         │    │  │  Outbound  │──┼────┤           │
│         │    │  │  (Repos)   │  │    │           │
│         │    │  └────────────┘  │    │           │
│         │    └────────┬─────────┘    │           │
│         │    ┌────────▼─────────┐    │           │
│         │    │     Domain       │    │           │
│         └───►│   (Entities)     │────┘           │
│              │  Pure dataclasses │                │
│              └──────────────────┘                │
└──────────────────────────────────────────────────┘
       Dependencies always point inward →
```

## Directory Structure

```
src/hexagonal/
├── main.py
├── domain/
│   └── entities/        # Pure Python dataclasses
│       ├── user.py
│       ├── post.py      # Post, Comment, Like
│       └── social.py    # Follow, Story, Message, Notification, Hashtag
├── ports/
│   ├── inbound/
│   │   └── use_cases.py  # Use case ABCs
│   └── outbound/
│       ├── repositories.py  # Repository ABCs (9 interfaces)
│       └── security.py      # SecurityPort ABC
├── application/
│   └── auth_service.py  # All service implementations
└── adapters/
    ├── inbound/
    │   └── api/
    │       ├── routers.py
    │       ├── schemas.py
    │       └── dependencies.py
    └── outbound/
        ├── persistence/
        │   ├── models.py        # SQLAlchemy ORM
        │   └── repositories.py  # Concrete repo implementations + mappers
        └── security/
            └── jwt_bcrypt.py    # SecurityPort implementation
```

## Key Characteristics

- **Domain entities are pure Python dataclasses** - no framework dependency, no SQLAlchemy, no Pydantic
- **Ports define ABCs** for both inbound (use cases) and outbound (repositories, security)
- **Adapters implement ports** - easily swappable (e.g., replace SQLAlchemy with MongoDB by writing a new outbound adapter)
- **Mapper functions** convert between domain entities and ORM models at the adapter boundary
- **Highly testable** - inject fake/in-memory adapters for fast, isolated testing

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
cd 02-hexagonal
uv sync
uv run uvicorn hexagonal.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Tests

```bash
uv run pytest tests/ -v
```

29 tests covering all domains.

## API Endpoints

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and receive JWT token |

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/me` | Get current user profile |
| GET | `/users/{user_id}` | Get user by ID |
| PUT | `/users/me` | Update current user profile |

### Posts

| Method | Path | Description |
|--------|------|-------------|
| POST | `/posts/` | Create a new post |
| GET | `/posts/` | List posts (feed) |
| GET | `/posts/{post_id}` | Get post by ID |
| DELETE | `/posts/{post_id}` | Delete a post |

### Comments

| Method | Path | Description |
|--------|------|-------------|
| POST | `/posts/{post_id}/comments` | Add comment to post |
| GET | `/posts/{post_id}/comments` | List comments on post |
| DELETE | `/comments/{comment_id}` | Delete a comment |

### Likes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/posts/{post_id}/like` | Like a post |
| DELETE | `/posts/{post_id}/like` | Unlike a post |

### Follows

| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/{user_id}/follow` | Follow a user |
| DELETE | `/users/{user_id}/follow` | Unfollow a user |
| GET | `/users/{user_id}/followers` | List followers |
| GET | `/users/{user_id}/following` | List following |

### Stories

| Method | Path | Description |
|--------|------|-------------|
| POST | `/stories/` | Create a story |
| GET | `/stories/` | List active stories |

### Messages

| Method | Path | Description |
|--------|------|-------------|
| POST | `/messages/` | Send a direct message |
| GET | `/messages/{user_id}` | Get conversation with user |

### Notifications

| Method | Path | Description |
|--------|------|-------------|
| GET | `/notifications/` | List notifications |
| PUT | `/notifications/{notification_id}/read` | Mark notification as read |

### Hashtags

| Method | Path | Description |
|--------|------|-------------|
| GET | `/hashtags/{tag}/posts` | Get posts by hashtag |
| GET | `/hashtags/trending` | Get trending hashtags |
