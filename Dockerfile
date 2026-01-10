FROM python:3.13-bookworm
ARG ENV

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies to /opt/venv so they persist after volume mount
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN if [ "$ENV" = "dev" ]; then \
        uv sync --frozen; \
    else \
        uv sync --frozen --no-dev; \
    fi

# Add venv to PATH
ENV PATH="/opt/venv/bin:$PATH"
