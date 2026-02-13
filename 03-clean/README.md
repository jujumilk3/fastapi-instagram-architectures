# Instagram Clone - Clean Architecture

Uncle Bob's Clean Architecture with 4 concentric layers. Dependencies flow strictly inward -- outer layers depend on inner layers, never the reverse. Each use case is a separate class with a single `execute()` method, enforcing the Single Responsibility Principle.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Frameworks & Drivers (outermost)                    │
│  SQLAlchemy, FastAPI, JWT, bcrypt                    │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │  Interface Adapters                          │    │
│  │  Controllers, Gateways, Schemas              │    │
│  │                                              │    │
│  │  ┌──────────────────────────────────────┐    │    │
│  │  │  Use Cases                           │    │    │
│  │  │  Application business rules          │    │    │
│  │  │                                      │    │    │
│  │  │  ┌──────────────────────────────┐    │    │    │
│  │  │  │  Entities (innermost)        │    │    │    │
│  │  │  │  Enterprise business rules   │    │    │    │
│  │  │  └──────────────────────────────┘    │    │    │
│  │  └──────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘

Dependency Rule: source code dependencies point INWARD only
```

## Directory Structure

```
src/clean/
├── main.py
├── entities/                  # Enterprise business rules (innermost)
│   ├── user.py
│   ├── post.py                # Post, Comment, Like
│   └── social.py              # Follow, Story, Message, Notification, Hashtag
├── use_cases/                 # Application business rules
│   ├── interfaces/
│   │   ├── repositories.py    # 9 repository ABCs
│   │   └── security.py        # SecurityGateway ABC
│   ├── auth/                  # RegisterUseCase, LoginUseCase, GetMeUseCase
│   ├── user/                  # GetProfile, UpdateProfile, GetFollowers, GetFollowing
│   ├── post/                  # CreatePost, GetPost, GetUserPosts, DeletePost
│   ├── comment/               # CreateComment, GetComments, DeleteComment
│   ├── like/                  # ToggleLike
│   ├── follow/                # FollowUser, UnfollowUser
│   ├── feed/                  # GetFeed
│   ├── story/                 # CreateStory, GetMyStories, GetStoryFeed, DeleteStory
│   ├── message/               # SendMessage, GetConversations, GetConversation, MarkRead
│   ├── notification/          # GetNotifications, MarkRead, MarkAllRead
│   └── search/                # SearchUsers, SearchHashtags, GetPostsByHashtag
├── interface_adapters/        # Controllers, gateways, presenters
│   ├── controllers/
│   │   └── routers.py         # FastAPI route handlers
│   ├── gateways/
│   │   └── repositories.py    # SQLAlchemy implementations
│   └── schemas/
│       └── schemas.py         # Pydantic DTOs
└── frameworks/                # External frameworks (outermost)
    ├── database.py            # SQLAlchemy engine + session
    ├── security.py            # JWT + bcrypt
    ├── models.py              # ORM models
    └── dependencies.py        # FastAPI DI wiring
```

## Key Characteristics

- **25 individual use case classes**, each with a single `execute()` method
- **Gateway interfaces (ABCs)** defined inside `use_cases/interfaces/` -- inner layers define contracts, outer layers implement them
- **Entities are pure Python dataclasses** (innermost layer, zero external dependencies)
- **ORM models live in `frameworks/`** (outermost) to keep inner layers framework-free
- **Mapper functions** in gateway repositories convert between ORM models and domain entities

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
cd 03-clean
uv sync
uv run uvicorn clean.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Tests

```bash
uv run pytest tests/ -v
```

29 tests covering all use cases.

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
