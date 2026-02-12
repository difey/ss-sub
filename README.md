# Clash Subscription Merger

A powerful, asyncio-based FastAPI service for merging multiple Clash subscriptions into a single, optimized configuration file.

## Features

- **Adaptive Merging**: Uses the first subscription's configuration (ports, DNS, basics) as the base template.
- **Namespacing**: Automatically prefixes proxies, proxy groups, and rules with the subscription name (e.g., `SubName_ProxyA`) to prevent conflicts.
- **Group Preservation**: Maintains the original relationship between proxies and their groups. Proxies are only added to their original groups (namespaced), ensuring clean separation.
- **Smart Rule Deduplication**: Filters out duplicate rules based on domain/IP, prioritizing the first subscription's rules.
- **Custom Rules Management**: 
  - Manage a list of custom rules via API.
  - Custom rules are upserted (updated/appended) and prepended to the final config, giving them highest priority.
- **Automated Scheduling**: Automatically refreshes and merges subscriptions every 10 minutes.
- **RESTful API**: Manage subscriptions, rules, and trigger merges manually.

## Installation

This project uses `uv` for dependency management.

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd ss_sub
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

## Usage

### Running the Server

Start the server using `uvicorn`:

```bash
uv run uvicorn src.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

### API Endpoints

Interactive documentation is available at `http://127.0.0.1:8000/docs`.

#### Subscription Management
- **List Subscriptions**: `GET /subscription/list`
- **Add Subscription**: `POST /subscription/`
  ```json
  {
    "url": "https://example.com/sub",
    "name": "MySub"
  }
  ```
- **Remove Subscription**: `DELETE /subscription/{sub_id}`
- **Manual Refresh**: `POST /subscription/refresh` - Triggers an immediate merge of all saved subscriptions.
- **Get Merged Config**: `GET /subscription/result` - Download the latest `merged.yaml`.
- **Direct Merge**: `GET /subscription/merge?urls=...` - Merge specific URLs on the fly without saving.

#### Custom Rules
- **Get Rules**: `GET /rules`
- **Update Rules**: `POST /rules/update`
  - Body: Raw text of rules (one per line).
  - Logic: Upserts rules. Existing rules with same type/value are updated; new ones appended.

## Configuration

Data is stored in the `data/` directory:
- `subscriptions.json`: List of saved subscriptions.
- `custom_rules.txt`: User-defined rules.
- `merged.yaml`: The generate merged configuration file.

## Development

- **Project Structure**:
    - `src/`: Source code.
        - `main.py`: App entry point.
        - `routers/`: API route definitions.
        - `services/`: Core logic (fetcher, merger, storage, scheduler).
        - `models/`: Pydantic models.
    - `data/`: Data storage (ignored by git).
