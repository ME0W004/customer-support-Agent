# Stage 1: Build the React Dashboard
FROM node:22-slim AS dashboard-builder
WORKDIR /build
COPY dashboard/package*.json ./
RUN npm install
COPY dashboard/ ./
RUN npm run build

# Stage 2: Python Application
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependencies definitions
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application source code
COPY app/ ./app
COPY scripts/ ./scripts
COPY evals/ ./evals

# Copy built frontend assets
COPY --from=dashboard-builder /build/dist ./dashboard/dist

EXPOSE 8000

# Default command runs the web API (can be overridden in docker-compose for poller)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
