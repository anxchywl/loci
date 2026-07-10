#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=${1:-${BACKUP_DIR:-/backups}}
LATEST=$(find "$BACKUP_DIR" -name "loci-*.dump" -type f -size +0c -print | sort | tail -n 1)

if [ -z "$LATEST" ]; then
  echo "error: no non-empty backup found in $BACKUP_DIR" >&2
  exit 1
fi

pg_restore --list "$LATEST" >/dev/null
echo "backup verified: $LATEST"
