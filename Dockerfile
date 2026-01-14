# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

ENV ORG_POETRY_VERSION=1.7.0
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_VIRTUALENVS_CREATE=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install "poetry==$ORG_POETRY_VERSION"

# Copy only pyproject.toml initially to cache deps
COPY pyproject.toml ./
# If poetry.lock exists, correct workflow would be to copy it too. 
# For now, we assume it's generated or we skip strict locking if missing.
# Running install without lock file will generate one in the container.
RUN poetry install --no-root --no-ansi

# Stage 2: Runtime
FROM python:3.11-slim as runtime

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY src ./src

# Create a user to avoid running as root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

ENTRYPOINT ["python", "-m", "src.main"]
