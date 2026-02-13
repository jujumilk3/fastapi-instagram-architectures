# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Overview

Instagram clone implemented with 12 different architecture patterns. Each is an independent FastAPI project with identical API endpoints, sharing no code.

## Architecture Status

| # | Architecture | Implementation | Tests | Status |
|---|---|---|---|---|
| 01 | Layered | Done | 33 passed | Ready |
| 02 | Hexagonal (Ports & Adapters) | Done | 34 passed | Ready |
| 03 | Clean Architecture | Done | 34 passed | Ready |
| 04 | Domain-Driven Design | Done | 33 passed | Ready |
| 05 | Modular Monolith | Done | 34 passed | Ready |
| 06 | CQRS + Event Sourcing | Done | 33 passed | Ready |
| 07 | Vertical Slice | Done | 34 passed | Ready |
| 08 | Event-Driven | Done | 37 passed | Ready |
| 09 | Microkernel (Plugin) | Done | 34 passed | Ready |
| 10 | Functional Core, Imperative Shell | Done | 65 passed | Ready |
| 11 | Actor Model | Done | 34 passed | Ready |
| 12 | Saga / Choreography | Done | 39 passed | Ready |

## Recent Changes

### 2026-02-13: Strengthen Tests and Documentation

**Documentation** - Fleshed out READMEs for architectures 07-12 (from ~16-25 lines to ~150+ lines each) with architecture ASCII diagrams, directory structures, key characteristics, tech stack, quick start, and API endpoint tables.

**Tests** - Added missing edge-case tests to architectures 01-07, 09-11:
- `test_followers_and_following_lists` - added to 01-07, 09-11
- `test_notification_created_on_follow` - added to 01-07, 09-11
- `test_notification_created_on_like` - added to 01-07, 09-11
- `test_mark_single_notification_read` - added to 01-07, 09-11
- `test_list_conversations` - added to 01-03, 05, 06, 10, 11
- `test_delete_post` 404 check - added to 01, 10, 11

## Common Tech Stack

- Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), aiosqlite
- Pydantic v2, python-jose (JWT), passlib[bcrypt], bcrypt<5.0.0
- uv package manager, hatchling build system
- pytest + pytest-asyncio + httpx for testing

## Common API Endpoints (all 12 projects)

- Auth: register, login, me
- Users: get profile, update me, get user posts/followers/following
- Posts: CRUD, likes (toggle), comments (CRUD)
- Follow: follow/unfollow
- Feed: get feed (posts from followed users)
- Stories: CRUD, story feed
- Messages: send, list conversations, get conversation, mark read
- Notifications: list, mark read, mark all read
- Search: users, hashtags, posts by hashtag

## How to Run Any Project

```bash
cd {project-dir}
uv sync
uv run uvicorn {package}.main:app --reload
# Visit http://localhost:8000/docs
```

## How to Run Tests

```bash
cd {project-dir}
uv run pytest tests/ -v
```
