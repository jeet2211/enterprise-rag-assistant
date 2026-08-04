#!/bin/sh
set -eu

mkdir -p /app/backend/uploads /app/backend/chroma_db
chown -R appuser:appgroup /app/backend/uploads /app/backend/chroma_db

# Run database migrations before starting the server
# Uses DATABASE_URL from environment (PostgreSQL in all envs)
gosu appuser alembic upgrade head

exec gosu appuser "$@"
