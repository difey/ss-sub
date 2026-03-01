# AGENTS.md - Development Guidelines for Clash Subscription Merger

## Project Overview

This is a Python FastAPI project for merging multiple Clash proxy subscriptions into a single configuration file. The project uses `uv` for dependency management and follows async Python patterns.

## Commands

### Running the Application

```bash
# Development server with auto-reload
uv run uvicorn src.main:app --reload

# Server runs at http://127.0.0.1:8000
# Swagger docs: http://127.0.0.1:8000/docs
# Frontend: http://127.0.0.1:8000/
```

### Testing

```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_merger.py

# Run a specific test
uv run pytest tests/test_merger.py::test_merge_clash_configs -v

# Run with output capture disabled (see print statements)
uv run pytest -s

# Run with coverage (if needed)
uv run pytest --cov=src --cov-report=term-missing
```

### Linting and Type Checking

This project uses standard Python tooling. Configure your editor to use:

- ** Ruff** for linting (fast, modern)
- ** pyright** or ** mypy** for type checking
- ** Black** for formatting (if not using Ruff)

```bash
# Install dev dependencies
uv sync --group dev

# Run ruff (if installed)
uv run ruff check src/
uv run ruff format src/

# Type checking
uv run pyright src/
```

### Docker

```bash
# Build Docker image
docker build -t clash-merger .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data clash-merger
```

## Code Style Guidelines

### General Principles

- Write clean, readable, and maintainable code
- Keep functions focused on a single responsibility
- Use async/await for I/O-bound operations (network requests, file I/O)
- Prefer explicit error handling over silent failures
- Add type hints to all function signatures

### Imports

```python
# Standard library first
import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

# Third-party packages
import httpx
import yaml
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

# Local imports (use absolute imports)
from src.services.merger import merge_clash_configs
from src.models.subscription import Subscription
```

### Type Hints

Always use type hints for function parameters and return types:

```python
# Good
async def fetch_subscription(url: str) -> str:
    ...

def merge_clash_configs(
    configs: List[Tuple[str, str]],
    custom_rules: Optional[List[str]] = None
) -> str:
    ...

# Avoid
async def fetch_subscription(url):
    ...
```

### Naming Conventions

- **Variables/functions**: snake_case (`fetch_subscription`, `merged_config`)
- **Classes**: PascalCase (`Subscription`, `StorageService`)
- **Constants**: SCREAMING_SNAKE_CASE (`DATA_DIR`, `MAX_RETRIES`)
- **Private methods**: prefix with underscore (`_save_subscriptions`)
- **Files**: snake_case (`subscription.py`, `test_merger.py`)

### Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import Optional
import uuid

class SubscriptionCreate(BaseModel):
    url: str
    name: Optional[str] = None

class Subscription(SubscriptionCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
```

### Error Handling

- Use exceptions for unexpected errors
- Return appropriate HTTP status codes in API endpoints
- Log errors with meaningful context
- Never expose internal error details to clients

```python
# Good example
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def get_merged_result():
    content = storage_service.get_merged_config()
    if not content:
        raise HTTPException(status_code=404, detail="No merged config found")
    return Response(content=content, media_type="application/x-yaml")
```

### Async/Await

- Use `asyncio.gather()` for concurrent operations
- Always use async HTTP clients (httpx.AsyncClient)
- Don't block the event loop with synchronous operations

```python
import asyncio

async def refresh_subscriptions():
    subs = storage_service.get_all_subscriptions()
    urls = [s.url for s in subs]
    
    # Fetch all subscriptions concurrently
    results = await asyncio.gather(
        *[fetch_subscription(url) for url in urls],
        return_exceptions=True
    )
    
    # Handle exceptions
    valid_configs = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Failed to fetch {urls[i]}: {result}")
            continue
        valid_configs.append((result, names[i]))
```

### Project Structure

```
src/
├── main.py              # FastAPI app entry point
├── routers/             # API route definitions
│   ├── subscription.py
│   └── rules.py
├── services/            # Business logic
│   ├── fetcher.py       # HTTP subscription fetching
│   ├── merger.py        # Clash config merging
│   ├── storage.py       # File storage
│   └── scheduler.py     # Background tasks
└── models/              # Pydantic models
    └── subscription.py

static/                  # Frontend files
data/                    # Runtime data (subscriptions.json, merged.yaml)
tests/                   # Test files
```

### Testing Guidelines

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test names: `test_merge_deduplicates_proxy_names`
- Use pytest fixtures for setup/teardown
- Test both success and error cases

```python
import pytest
from src.services.merger import merge_clash_configs

def test_merge_clash_configs():
    config1 = """..."""
    config2 = """..."""
    
    merged_yaml = merge_clash_configs([(config1, "Sub1"), (config2, "Sub2")])
    merged_config = yaml.safe_load(merged_yaml)
    
    assert len(merged_config["proxies"]) == 4
    assert "Sub1_ProxyA" in [p["name"] for p in merged_config["proxies"]]
```

### Git Conventions

- Write clear, concise commit messages
- Use present tense: "Add feature" not "Added feature"
- Reference issues in commits when applicable
- Don't commit secrets or sensitive data

### Docker Considerations

- Keep images small (use Alpine base if possible)
- Don't run as root in containers
- Use environment variables for configuration
- Mount volumes for persistent data

## API Reference

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/subscription/list` | List all subscriptions |
| POST | `/subscription/` | Add subscription |
| DELETE | `/subscription/{id}` | Remove subscription |
| POST | `/subscription/refresh` | Trigger merge |
| GET | `/subscription/result` | Download merged config |
| GET | `/rules` | Get custom rules |
| POST | `/rules/update` | Update custom rules |

### Data Files

Data is stored in `data/` directory:
- `subscriptions.json` - Saved subscription list
- `custom_rules.txt` - User-defined rules
- `merged.yaml` - Generated merged configuration
