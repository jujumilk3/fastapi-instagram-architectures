# Instagram Clone - Microkernel (Plugin) Architecture

A minimal core system provides infrastructure (DB, auth, plugin registry). Each domain feature is a plugin that registers itself with the core via a `Plugin` ABC and `PluginRegistry`.

## Setup

```bash
uv sync
```

## Run

```bash
uv run uvicorn microkernel.main:app --reload
```

## Test

```bash
uv run pytest tests/ -v
```
