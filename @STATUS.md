# Project Status

**Last Updated:** 2026-02-13 KST
**Last Author:** Claude Code

## Overview

Instagram clone implemented with 12 different architecture patterns. Each is an independent FastAPI project with identical API endpoints, sharing no code.

## Architecture Status

| # | Architecture | Implementation | Tests | Status |
|---|---|---|---|---|
| 01 | Layered | Done | 29 passed | Ready |
| 02 | Hexagonal (Ports & Adapters) | Done | 29 passed | Ready |
| 03 | Clean Architecture | Done | 29 passed | Ready |
| 04 | Domain-Driven Design | Done | 29 passed | Ready |
| 05 | Modular Monolith | Done | 30 passed | Ready |
| 06 | CQRS + Event Sourcing | Done | 29 passed | Ready |
| 07 | Vertical Slice | Done | 30 passed | Ready |
| 08 | Event-Driven | Done | 37 passed | Ready |
| 09 | Microkernel (Plugin) | Done | 30 passed | Ready |
| 10 | Functional Core, Imperative Shell | Done | 60 passed | Ready |
| 11 | Actor Model | Done | 29 passed | Ready |
| 12 | Saga / Choreography | Done | 39 passed | Ready |

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
