# FastAPI Instagram Architectures

Instagram의 핵심 도메인을 **12가지 아키텍처 패턴**으로 각각 구현한 학습용 프로젝트. 동일한 API 엔드포인트를 유지하면서 아키텍처 구조만 다르게 설계하여 각 패턴의 장단점을 직접 비교할 수 있다.

## Architectures

| # | Architecture | Description | Complexity |
|---|---|---|---|
| [01](./01-layered/) | **Layered** | 수평 슬라이싱. API → Service → Repository → Model | Low |
| [02](./02-hexagonal/) | **Hexagonal (Ports & Adapters)** | 의존성이 항상 도메인을 향함. Port(ABC) + Adapter(구현체) | Medium |
| [03](./03-clean/) | **Clean Architecture** | 4개 동심원 레이어. Use Case별 1클래스 1메서드(execute) | Medium-High |
| [04](./04-ddd/) | **Domain-Driven Design** | Rich Domain Model. Aggregate, Value Object, Domain Event | High |
| [05](./05-modular-monolith/) | **Modular Monolith** | 기능별 수직 슬라이싱. 모듈 = 잠재적 마이크로서비스 경계 | Medium |
| [06](./06-cqrs-event-sourcing/) | **CQRS + Event Sourcing** | 쓰기/읽기 경로 분리. Append-only Event Store + Projection | High |
| [07](./07-vertical-slice/) | **Vertical Slice** | Use Case별 완전 독립 슬라이스. Request → Mediator → Handler → Response | Medium |
| [08](./08-event-driven/) | **Event-Driven** | 이벤트 브로커 중심. Producer → Event Channel → Consumer | Medium-High |
| [09](./09-microkernel/) | **Microkernel (Plugin)** | Core + Plugin Registry. 각 도메인이 플러그인으로 자체 등록 | Medium |
| [10](./10-functional-core-imperative-shell/) | **Functional Core, Imperative Shell** | 순수 함수(비즈니스 로직) + 불순 셸(IO). 사이드이펙트 경계 분리 | Medium |
| [11](./11-actor-model/) | **Actor Model** | Actor별 독립 상태 + 메시지 패싱. asyncio.Queue 메일박스 | Medium-High |
| [12](./12-saga-choreography/) | **Saga / Choreography** | 분산 트랜잭션 관리. 보상 액션 + 이벤트 기반 코레오그래피 | High |

## Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI + Pydantic v2
- **ORM**: SQLAlchemy 2.0 (async) + aiosqlite
- **Auth**: python-jose (JWT) + passlib[bcrypt]
- **Package Manager**: uv
- **Testing**: pytest + pytest-asyncio + httpx

## Quick Start

```bash
# 원하는 아키텍처 디렉토리로 이동
cd 01-layered

# 의존성 설치
uv sync

# 서버 실행
uv run uvicorn layered.main:app --reload

# Swagger UI 확인
open http://localhost:8000/docs

# 테스트 실행
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

Instagram의 핵심 기능을 10개 도메인으로 구성:

- **User** - 회원가입, 로그인, 프로필
- **Post** - 게시글 CRUD, 이미지 URL
- **Comment** - 게시글 댓글
- **Like** - 좋아요 토글
- **Follow** - 팔로우/언팔로우
- **Feed** - 팔로잉 유저의 게시글 피드
- **Story** - 24시간 스토리
- **Message** - 1:1 다이렉트 메시지
- **Notification** - 알림 (좋아요, 댓글, 팔로우)
- **Search** - 유저/해시태그/게시글 검색

## API Endpoints

모든 12개 프로젝트가 동일한 API 계약을 공유한다:

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
| 01-layered | 29 passed | ~2s |
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
| Vertical Slice | Feature 단위 독립 개발, 대규모 팀 협업 |
| Event-Driven | 비동기 사이드이펙트, 컴포넌트 디커플링 |
| Microkernel | 플러그인 기반 확장, 동적 기능 추가/제거 |
| Functional Core | 테스트 용이성 극대화, 순수 함수 중심 설계 |
| Actor Model | 동시성 제어, 메시지 기반 통신, 독립 상태 관리 |
| Saga / Choreography | 분산 트랜잭션, 보상 패턴, 멀티스텝 워크플로우 |
