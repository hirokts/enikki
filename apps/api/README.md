# Backend API

This project uses `uv` for dependency management and running the application.

## Setup

1. Install `uv`: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
2. Install dependencies:
   ```bash
   uv sync
   ```

## Development

### Option 1: Docker Compose (Recommended)

From the project root directory:

```bash
docker compose up
```

The API will be available at `http://localhost:8000`.

### Option 2: Local uv

```bash
uv run uvicorn src.main:app --reload
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `GCP_PROJECT_ID` | Google Cloud Project ID |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account key JSON (local dev) |

## Structure

- `src/main.py`: Application entry point
- `src/api/`: Application logic (Auth, Summary, etc.)
