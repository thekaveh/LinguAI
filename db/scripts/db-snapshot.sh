#!/usr/bin/env bash
set -euo pipefail

# Re-snapshots the running database into the seed file consumed by Postgres'
# docker-entrypoint-initdb.d on a fresh data volume.
#
# Usage (from host):
#   docker exec db sh ./scripts/db-snapshot.sh
#
# Environment variables (provided by docker-compose via .env):
#   POSTGRES_USER          superuser the dump is taken as
#   POSTGRES_DB            database to dump
#   POSTGRES_APP_USER      application-role name prepended to the dump
#   POSTGRES_APP_PASSWORD  application-role password prepended to the dump

DUMP_FILE="/docker-entrypoint-initdb.d/linguai_db_ss.sql"
TMP_FILE="${DUMP_FILE}.tmp"

DB_USER="${POSTGRES_USER:?POSTGRES_USER not set}"
DB_NAME="${POSTGRES_DB:?POSTGRES_DB not set}"
APP_ROLE="${POSTGRES_APP_USER:?POSTGRES_APP_USER not set}"
APP_PASS="${POSTGRES_APP_PASSWORD:?POSTGRES_APP_PASSWORD not set}"

rm -f "$TMP_FILE"
pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner > "$DUMP_FILE"
{
  printf "CREATE ROLE %s WITH LOGIN PASSWORD '%s';\n" "$APP_ROLE" "$APP_PASS"
  cat "$DUMP_FILE"
} > "$TMP_FILE"
mv "$TMP_FILE" "$DUMP_FILE"
