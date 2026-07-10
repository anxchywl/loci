#!/usr/bin/env bash
set -euo pipefail

# daily postgres backup — runs inside the backup container via cron

BACKUP_DIR=${BACKUP_DIR:-/backups}
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-14}
STAMP=$(date +%Y%m%d-%H%M%S)
FILE="$BACKUP_DIR/loci-$STAMP.dump"

pg_dump \
  --host="${POSTGRES_HOST:-postgres}" \
  --username="${POSTGRES_USER:-loci}" \
  --dbname="${POSTGRES_DB:-loci}" \
  --format=custom \
  --file="$FILE"

pg_restore --list "$FILE" >/dev/null

find "$BACKUP_DIR" -name "loci-*.dump" -mtime "+$RETENTION_DAYS" -delete

echo "backup written: $FILE ($(du -h "$FILE" | cut -f1))"
