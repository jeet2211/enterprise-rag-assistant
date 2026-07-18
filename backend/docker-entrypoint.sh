#!/bin/sh
set -eu

mkdir -p /app/backend/uploads /app/backend/chroma_db /app/backend/data
chown -R appuser:appgroup /app/backend/uploads /app/backend/chroma_db /app/backend/data

exec gosu appuser "$@"
