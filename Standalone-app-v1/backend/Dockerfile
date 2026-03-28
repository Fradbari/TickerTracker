# TickerTracker Backend — Production Dockerfile
# Python 3.13 slim image
FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies needed by some Python packages, plus PostgreSQL client for backups
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in a separate layer (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project (src, alembic, alembic.ini, pyproject.toml, scripts, etc.)
COPY . .

EXPOSE 8000

# Run Alembic migrations then start the FastAPI server without hot-reload (optimized for prod)
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
