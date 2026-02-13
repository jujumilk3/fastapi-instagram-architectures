# Instagram Clone - Actor Model Architecture

FastAPI Instagram clone implementing the Actor Model architecture pattern.

Each domain concept is an independent Actor with private state, processing messages one at a time through an asyncio.Queue mailbox. Actors communicate via addressed messages (not broadcast), providing built-in concurrency safety.

## Setup

```bash
uv sync
uv run fastapi dev src/actor_model/main.py
```

## Test

```bash
uv run pytest tests/ -v
```
