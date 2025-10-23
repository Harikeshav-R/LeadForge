# Stage 1: Base image with uv installer
FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /root

# Make gemini folder on container
RUN mkdir -p /root/.gemini

# Copy gemini auth files
COPY ./.gemini /root/.gemini

WORKDIR /builder


FROM base AS system-deps

# Install node and npm
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install gemini-cli
RUN npm install -g @google/gemini-cli


FROM system-deps AS python-deps

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

# Install deps.
RUN uv sync --frozen --no-cache


FROM python-deps AS sources

# Copy project sources
COPY . .


# Stage 2: Development image
FROM sources AS dev
CMD ["uv", "run" ,"uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]


# Stage 3: Production image
FROM sources AS prod
CMD ["uv", "run" ,"uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "4"]