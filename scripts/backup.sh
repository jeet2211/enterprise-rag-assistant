#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Enterprise RAG Assistant — Daily Postgres Backup Script
# Schedule with cron: 0 2 * * * /opt/rag-assistant/scripts/backup.sh
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

COMPOSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd)"
BACKUP_DIR="/backups/ragdb"
RETENTION_DAYS=30
DATE=$(date +%Y-%m-%d_%H-%M-%S)
FILE="${BACKUP_DIR}/ragdb_${DATE}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] Starting Postgres backup..."

docker compose -f "${COMPOSE_DIR}/docker-compose.yml" \
               -f "${COMPOSE_DIR}/docker-compose.prod.yml" \
               exec -T postgres \
               pg_dump -U raguser ragdb \
  | gzip > "${FILE}"

echo "[$(date)] Backup written to ${FILE} ($(du -h "${FILE}" | cut -f1))"

# Prune old backups
find "${BACKUP_DIR}" -name 'ragdb_*.sql.gz' -mtime +"${RETENTION_DAYS}" -delete
echo "[$(date)] Pruned backups older than ${RETENTION_DAYS} days"

# Also backup ChromaDB volume (cold copy)
CHROMA_BACKUP="${BACKUP_DIR}/chroma_${DATE}.tar.gz"
docker run --rm \
  -v enterprise-rag-assistent_backend_chroma:/data:ro \
  -v "${BACKUP_DIR}":/backup \
  alpine tar czf "/backup/chroma_${DATE}.tar.gz" -C /data . 2>/dev/null || true

echo "[$(date)] Backup complete."
