# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: DDD Architecture Fully Implemented
- ✅ Domain layer with rich aggregates, value objects, and domain events
- ✅ Application layer with service classes per bounded context
- ✅ Infrastructure layer with ORM models, mapper, repositories, API
- ✅ All 36 API endpoints matching other architectures
- ✅ uv sync successful, all routes verified

## Next Actions (Priority Order)

1. **[MEDIUM]** Add unit tests for domain aggregates and value objects
2. **[LOW]** Add integration tests for API endpoints

## Code Location Map

### Domain Layer (`src/ddd/domain/`)
- `shared/entity.py` - Base Entity, AggregateRoot classes
- `shared/value_object.py` - Base ValueObject class
- `shared/event.py` - Domain events (UserRegistered, PostCreated, PostLiked, etc.)
- `user/aggregate.py` - UserAggregate with create(), update_profile(), collect_events()
- `user/value_objects.py` - Email, Username value objects (frozen, validated)
- `user/repository.py` - UserRepository ABC
- `post/aggregate.py` - PostAggregate with add_comment(), toggle_like(), extract_hashtags()
- `post/entities.py` - Comment, Like child entities
- `post/repository.py` - PostRepository, CommentRepository, LikeRepository ABCs
- `social/aggregate.py` - Follow, Story entities
- `social/repository.py` - FollowRepository, StoryRepository ABCs
- `messaging/aggregate.py` - Message entity
- `messaging/repository.py` - MessageRepository ABC
- `notification/entity.py` - Notification entity
- `notification/repository.py` - NotificationRepository ABC
- `hashtag/entity.py` - Hashtag entity
- `hashtag/repository.py` - HashtagRepository ABC

### Application Layer (`src/ddd/application/`)
- `auth/service.py` - AuthApplicationService (register, login, get_me)
- `user/service.py` - UserApplicationService (profile, update, followers/following)
- `post/service.py` - PostApplicationService, CommentApplicationService, LikeApplicationService
- `social/service.py` - FollowApplicationService, StoryApplicationService
- `feed/service.py` - FeedApplicationService
- `messaging/service.py` - MessageApplicationService
- `notification/service.py` - NotificationApplicationService
- `search/service.py` - SearchApplicationService

### Infrastructure Layer (`src/ddd/infrastructure/`)
- `database.py` - SQLAlchemy async engine + session factory
- `security.py` - SecurityProvider (JWT + bcrypt)
- `orm/models.py` - SQLAlchemy ORM models (singular snake_case tables)
- `orm/mapper.py` - Domain <-> ORM mapping functions
- `repositories/user_repository.py` - SqlAlchemyUserRepository
- `repositories/post_repository.py` - SqlAlchemyPostRepository, CommentRepository, LikeRepository
- `repositories/social_repository.py` - SqlAlchemyFollowRepository, StoryRepository
- `repositories/message_repository.py` - SqlAlchemyMessageRepository
- `repositories/notification_repository.py` - SqlAlchemyNotificationRepository
- `repositories/hashtag_repository.py` - SqlAlchemyHashtagRepository
- `api/schemas.py` - Pydantic DTOs
- `api/routers.py` - FastAPI route handlers
- `api/dependencies.py` - DI wiring

### Entry Point
- `main.py` - FastAPI app with lifespan

## How to Work on This

### Setup
```bash
cd /Users/gyu/Projects/fastapi-instagram-architectures/04-ddd
uv sync
```

### Run
```bash
uv run uvicorn ddd.main:app --reload
```

### Verify
```bash
uv run python -c "from ddd.main import app; print('OK')"
```

### Current Tech Stack
- Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), aiosqlite
- passlib[bcrypt] + python-jose for auth
- Pydantic 2.0 for DTOs

## Architecture Decisions
- Rich domain model: Aggregates have behavior (update_profile, add_comment, toggle_like)
- Value Objects: Email, Username are immutable and validated on creation
- Domain Events: Collected in aggregates, processed after persistence
- Repository pattern: ABCs in domain, implementations in infrastructure
- Mapper layer: Explicit domain <-> ORM mapping (no ORM in domain)
- Singular snake_case table names
- All datetimes timezone-aware (UTC)
