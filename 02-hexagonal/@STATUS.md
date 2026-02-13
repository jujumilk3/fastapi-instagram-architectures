# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-02-13: Full Hexagonal Architecture Implemented + Tested
- Domain entities as pure dataclasses
- Ports (ABCs) for inbound use cases and outbound repositories/security
- Adapters: API routers (inbound), SQLAlchemy repos + JWT/bcrypt (outbound)
- 29 API tests passing
- bcrypt<5.0.0 pinned for passlib compatibility

## Code Location Map

### Domain (`src/hexagonal/domain/entities/`)
- `user.py`, `post.py` (Post, Comment, Like), `social.py` (Follow, Story, Message, Notification, Hashtag)

### Ports
- `ports/outbound/repositories.py` - 9 repository ABCs
- `ports/outbound/security.py` - SecurityPort ABC
- `ports/inbound/use_cases.py` - All use case ABCs

### Application (`src/hexagonal/application/`)
- `auth_service.py` - All service implementations

### Adapters
- `adapters/outbound/persistence/models.py` - ORM models
- `adapters/outbound/persistence/repositories.py` - Repository implementations + mappers
- `adapters/outbound/security/jwt_bcrypt.py` - JWT + bcrypt implementation
- `adapters/inbound/api/routers.py` - FastAPI routes
- `adapters/inbound/api/schemas.py` - Pydantic DTOs
- `adapters/inbound/api/dependencies.py` - DI wiring

### Tests (`tests/`)
- `conftest.py` - Test DB, fixtures
- `test_api.py` - 29 tests across 11 test classes

## How to Work on This

```bash
cd 02-hexagonal
uv sync
uv run uvicorn hexagonal.main:app --reload
uv run pytest tests/ -v
```

## Architecture Decisions

- Dependencies always point inward (adapters -> application -> domain)
- Domain entities are pure Python dataclasses (no framework dependency)
- Mapper functions convert between domain entities and ORM models
- Ports defined as ABCs, adapters implement them
