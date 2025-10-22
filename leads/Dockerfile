# Stage 1: Base image with uv installer
FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /leads

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

# Install deps.
RUN uv sync --frozen --no-cache

# Install chromium
RUN apt-get update && uv run playwright install --with-deps chromium

# Copy project sources
COPY . .

# Stage 2: Development image
FROM base AS dev
CMD ["uv", "run" ,"uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]


# Stage 3: Production image
FROM base AS prod
CMD ["uv", "run" ,"uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]