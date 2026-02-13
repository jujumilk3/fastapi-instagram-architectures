# Instagram Clone - Layered Architecture

Horizontal layering with strict downward dependency. The simplest and most traditional architecture pattern where each layer only communicates with the layer directly below it.

## Architecture

```
┌─────────────────────────────────┐
│   API Layer (Presentation)      │  FastAPI routers, request/response
├─────────────────────────────────┤
│   Service Layer (Business Logic)│  Use cases, validation, orchestration
├─────────────────────────────────┤
│   Repository Layer (Data Access)│  Database queries, CRUD operations
├─────────────────────────────────┤
│   Model Layer (ORM)             │  SQLAlchemy models, table definitions
└─────────────────────────────────┘
         ↓ Dependencies flow downward only
```

## Directory Structure

```
src/layered/
├── main.py
├── config.py
├── database.py
├── security.py
├── models/          # SQLAlchemy ORM models
│   ├── base.py      # DeclarativeBase + TimestampMixin
│   ├── user.py
│   ├── post.py
│   ├── comment.py
│   ├── like.py
│   ├── follow.py
│   ├── story.py
│   ├── message.py
│   ├── notification.py
│   └── hashtag.py
├── repositories/    # Data access layer
├── services/        # Business logic layer
├── schemas/         # Pydantic DTOs
└── api/             # FastAPI routers
```

## Key Characteristics

- **Strict horizontal slicing** - each layer only depends on the layer directly below
- **Anemic domain model** - data-only ORM models with no business logic
- **Simple and easy to understand** - clear separation of concerns through layering
- **Can lead to "lasagna code"** - excessive layering in large projects where every change requires touching all layers

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
cd 01-layered
uv sync
uv run uvicorn layered.main:app --reload
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
