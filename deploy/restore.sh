#!/usr/bin/env bash
set -euo pipefail

# restore a backup into the production database — destructive, asks for confirmation
# usage: deploy/restore.sh /opt/loci/backups/loci-YYYYMMDD-HHMMSS.dump

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f $REPO_DIR/docker/docker-compose.prod.yml --env-file $REPO_DIR/.env"

DUMP_FILE=${1:?usage: restore.sh <path-to-dump-file>}

if [ ! -f "$DUMP_FILE" ]; then
  echo "error: $DUMP_FILE not found" >&2
  exit 1
fi

$COMPOSE exec -T postgres pg_restore --list < "$DUMP_FILE" >/dev/null

echo "this will replace the production database contents"
read -r -p "type 'restore' to continue: " CONFIRM
if [ "$CONFIRM" != "restore" ]; then
  echo "aborted"
  exit 1
fi

$COMPOSE exec -T postgres sh -c \
  'pg_restore --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --clean --if-exists --no-owner' \
  < "$DUMP_FILE"

$COMPOSE run --rm --no-deps api alembic upgrade head

echo "restore complete from $DUMP_FILE"
