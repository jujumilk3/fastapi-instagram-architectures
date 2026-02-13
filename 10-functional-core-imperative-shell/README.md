# Instagram Clone - Functional Core, Imperative Shell Architecture

Business logic lives in **pure functions** (no side effects, no DB, no IO). All IO (database, HTTP, JWT) is pushed to the **imperative shell** at the edges.

## Quick Start

```bash
uv sync
uv run uvicorn functional_core.main:app --reload
```

## Run Tests

```bash
uv run pytest tests/ -v
```
