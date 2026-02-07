# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies (without project itself)
RUN uv sync --frozen --no-install-project --no-dev

# Copy the application code
COPY . /app

# Sync the project (install the project itself)
RUN uv sync --frozen --no-dev

# Default port for Cloud Run
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run the application (use PORT env var for Cloud Run compatibility)
CMD ["sh", "-c", "uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT"]
