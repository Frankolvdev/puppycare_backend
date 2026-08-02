#!/bin/sh
set -eu

if [ "${RUN_DB_MIGRATIONS:-false}" = "true" ]; then
    echo "Applying Alembic database migrations..."
    python -m alembic upgrade head
fi

echo "Starting PuppyCare on port ${PORT:-8000}..."
exec python -m uvicorn app.main:app         --host 0.0.0.0         --port "${PORT:-8000}"         --proxy-headers         --forwarded-allow-ips="*"
