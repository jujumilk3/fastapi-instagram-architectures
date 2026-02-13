# FastAPI Instagram Architectures

A learning project implementing Instagram's core domain with **12 architecture patterns**. All projects share identical API endpoints while differing only in architectural structure, allowing direct comparison of each pattern's strengths and weaknesses.

## Architectures

| # | Architecture | Description | Complexity |
|---|---|---|---|
| [01](./01-layered/) | **Layered** | Horizontal slicing. API → Service → Repository → Model | Low |
| [02](./02-hexagonal/) | **Hexagonal (Ports & Adapters)** | Dependencies always point toward the domain. Port(ABC) + Adapter(impl) | Medium |
| [03](./03-clean/) | **Clean Architecture** | 4 concentric layers. One class per Use Case with single execute() method | Medium-High |
| [04](./04-ddd/) | **Domain-Driven Design** | Rich Domain Model. Aggregate, Value Object, Domain Event | High |
| [05](./05-modular-monolith/) | **Modular Monolith** | Vertical slicing by feature. Module = potential microservice boundary | Medium |
| [06](./06-cqrs-event-sourcing/) | **CQRS + Event Sourcing** | Write/read path separation. Append-only Event Store + Projection | High |
| [07](./07-vertical-slice/) | **Vertical Slice** | Fully independent slice per use case. Request → Mediator → Handler → Response | Medium |
| [08](./08-event-driven/) | **Event-Driven** | Event broker centric. Producer → Event Channel → Consumer | Medium-High |
| [09](./09-microkernel/) | **Microkernel (Plugin)** | Core + Plugin Registry. Each domain self-registers as a plugin | Medium |
| [10](./10-functional-core-imperative-shell/) | **Functional Core, Imperative Shell** | Pure functions (business logic) + impure shell (IO). Side-effect boundary separation | Medium |
| [11](./11-actor-model/) | **Actor Model** | Independent state per actor + message passing. asyncio.Queue mailbox | Medium-High |
| [12](./12-saga-choreography/) | **Saga / Choreography** | Distributed transaction management. Compensating actions + event-based choreography | High |

## Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI + Pydantic v2
- **ORM**: SQLAlchemy 2.0 (async) + aiosqlite
- **Auth**: python-jose (JWT) + passlib[bcrypt]
- **Package Manager**: uv
- **Testing**: pytest + pytest-asyncio + httpx

## Quick Start

```bash
# Navigate to the desired architecture directory
cd 01-layered

# Install dependencies
uv sync

# Run the server
uv run uvicorn layered.main:app --reload

# Open Swagger UI
open http://localhost:8000/docs

# Run tests
uv run pytest tests/ -v
```

### Package Names by Architecture

| Directory | Package | uvicorn Command |
|---|---|---|
| `01-layered` | `layered` | `uv run uvicorn layered.main:app --reload` |
| `02-hexagonal` | `hexagonal` | `uv run uvicorn hexagonal.main:app --reload` |
| `03-clean` | `clean` | `uv run uvicorn clean.main:app --reload` |
| `04-ddd` | `ddd` | `uv run uvicorn ddd.main:app --reload` |
| `05-modular-monolith` | `modular_monolith` | `uv run uvicorn modular_monolith.main:app --reload` |
| `06-cqrs-event-sourcing` | `cqrs_es` | `uv run uvicorn cqrs_es.main:app --reload` |
| `07-vertical-slice` | `vertical_slice` | `uv run uvicorn vertical_slice.main:app --reload` |
| `08-event-driven` | `event_driven` | `uv run uvicorn event_driven.main:app --reload` |
| `09-microkernel` | `microkernel` | `uv run uvicorn microkernel.main:app --reload` |
| `10-functional-core-imperative-shell` | `functional_core` | `uv run uvicorn functional_core.main:app --reload` |
| `11-actor-model` | `actor_model` | `uv run uvicorn actor_model.main:app --reload` |
| `12-saga-choreography` | `saga_choreography` | `uv run uvicorn saga_choreography.main:app --reload` |

## Domain

Instagram's core features organized into 10 domains:

- **User** - Registration, login, profile
- **Post** - Post CRUD, image URL
- **Comment** - Post comments
- **Like** - Like toggle
- **Follow** - Follow/unfollow
- **Feed** - Feed of posts from followed users
- **Story** - 24-hour stories
- **Message** - 1:1 direct messages
- **Notification** - Notifications (likes, comments, follows)
- **Search** - User/hashtag/post search

## API Endpoints

All 12 projects share the same API contract:

```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me

GET    /api/users/{id}
PUT    /api/users/me
GET    /api/users/{id}/posts
GET    /api/users/{id}/followers
GET    /api/users/{id}/following

POST   /api/posts
GET    /api/posts/{id}
DELETE /api/posts/{id}
POST   /api/posts/{id}/likes
GET    /api/posts/{id}/comments
POST   /api/posts/{id}/comments
DELETE /api/posts/comments/{id}

POST   /api/follow/{user_id}
DELETE /api/follow/{user_id}

GET    /api/feed

POST   /api/stories
GET    /api/stories
GET    /api/stories/feed
DELETE /api/stories/{id}

POST   /api/messages
GET    /api/messages
GET    /api/messages/{user_id}
POST   /api/messages/{sender_id}/read

GET    /api/notifications
POST   /api/notifications/{id}/read
POST   /api/notifications/read-all

GET    /api/search/users?q=
GET    /api/search/hashtags?q=
GET    /api/search/posts/hashtag/{tag}
```

## Test Results

| Architecture | Tests | Time |
|---|---|---|
| 01-layered | 29 passed | ~9s |
| 02-hexagonal | 29 passed | ~2s |
| 03-clean | 29 passed | ~9s |
| 04-ddd | 29 passed | ~9s |
| 05-modular-monolith | 30 passed | ~9s |
| 06-cqrs-event-sourcing | 29 passed | ~9s |
| 07-vertical-slice | 30 passed | ~9s |
| 08-event-driven | 37 passed | ~10s |
| 09-microkernel | 30 passed | ~9s |
| 10-functional-core-imperative-shell | 60 passed | ~9s |
| 11-actor-model | 29 passed | ~8s |
| 12-saga-choreography | 39 passed | ~11s |

## Architecture Comparison

### Dependency Direction

```
01-layered:        API → Service → Repository → Model (top-down)
02-hexagonal:      Adapters → Ports → Domain (outside-in)
03-clean:          Frameworks → Adapters → Use Cases → Entities (outside-in, 4 layers)
04-ddd:            Infrastructure → Application → Domain (outside-in, rich model)
05-modular:        Module[Router → Service → Model] (vertical per feature)
06-cqrs-es:        Command → Handler → Aggregate → EventStore → Projection (event flow)
07-vertical-slice: Router → Mediator → Handler[Request→DB→Response] (per use case)
08-event-driven:   Producer → EventBroker → Consumer (pub/sub decoupling)
09-microkernel:    Core[Registry] ← Plugin[Router+Service+Model] (plugin self-registration)
10-functional:     Router → Shell[IO] → Core[Pure Functions] → Shell[IO] (purity boundary)
11-actor-model:    Router → Message → Actor[Mailbox → receive()] (message passing)
12-saga:           Router → SagaExecutor[Step → Step → ...] + Compensate on failure (saga flow)
```

### Model Strategy

| Architecture | Domain Model | ORM Model | Mapping |
|---|---|---|---|
| 01-layered | Same (anemic ORM) | SQLAlchemy | None needed |
| 02-hexagonal | Python dataclass | SQLAlchemy | Mapper functions |
| 03-clean | Python dataclass | SQLAlchemy | Mapper functions |
| 04-ddd | Rich aggregate (dataclass) | SQLAlchemy | Mapper functions |
| 05-modular | Same (anemic ORM) | SQLAlchemy | None needed |
| 06-cqrs-es | Aggregate (write) + Projection (read) | SQLAlchemy | Event → Projection |
| 07-vertical-slice | Same (anemic ORM) | SQLAlchemy | None needed |
| 08-event-driven | Same (anemic ORM) | SQLAlchemy | None needed |
| 09-microkernel | Same (anemic ORM) | SQLAlchemy | None needed |
| 10-functional | Same (anemic ORM) | SQLAlchemy | None needed |
| 11-actor-model | Same (anemic ORM) | SQLAlchemy | None needed |
| 12-saga | Same (anemic ORM) | SQLAlchemy | None needed |

### When to Use

| Architecture | Best For |
|---|---|
| Layered | Small apps, CRUD-heavy, learning |
| Hexagonal | Testability, swappable infrastructure |
| Clean | Complex business rules, granular use cases |
| DDD | Complex domains, team collaboration |
| Modular Monolith | Growing monolith, future microservice split |
| CQRS + ES | Audit trails, event replay, read/write scale separately |
| Vertical Slice | Independent feature development, large team collaboration |
| Event-Driven | Async side effects, component decoupling |
| Microkernel | Plugin-based extensibility, dynamic feature add/remove |
| Functional Core | Maximum testability, pure function-centric design |
| Actor Model | Concurrency control, message-based communication, independent state management |
| Saga / Choreography | Distributed transactions, compensation patterns, multi-step workflows |
