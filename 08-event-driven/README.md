# 08 - Event-Driven Architecture

Instagram clone API using Event-Driven Architecture with FastAPI.

## Architecture

All inter-component communication happens through events. Components are decoupled producers and consumers connected via an in-memory event broker. The system reacts to events rather than direct method calls.

- **Producers**: Handle primary actions (DB writes) and publish events
- **Consumers**: React to events asynchronously (notifications, hashtag extraction)
- **Queries**: Separate read-only functions for GET endpoints
- **Event Broker**: In-memory pub/sub connecting producers to consumers

## Setup

```bash
uv sync
uv run uvicorn event_driven.main:app --reload
```

## Test

```bash
uv run pytest tests/ -v
```
