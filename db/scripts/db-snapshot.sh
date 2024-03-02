#!/bin/bash

# pg_dump -U linguai_db_user -d linguai_db --no-owner > /docker-entrypoint-initdb.d/linguai_db_ss.sql && { echo "CREATE ROLE linguai_app WITH LOGIN PASSWORD 'linguai_app_pass';"; cat /docker-entrypoint-initdb.d/linguai_db_ss.sql; } > /docker-entrypoint-initdb.d/linguai_db_ss.sql.tmp && mv /docker-entrypoint-initdb.d/linguai_db_ss.sql.tmp /docker-entrypoint-initdb.d/linguai_db_ss.sql

DUMP_FILE="/docker-entrypoint-initdb.d/linguai_db_ss.sql"

DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"
APP_ROLE="${POSTGRES_APP_USER}"
APP_PASS="${POSTGRES_APP_PASSWORD}"

echo $APP_PASS

# Perform the database dump
pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner > "$DUMP_FILE" && {
  echo "CREATE ROLE $APP_ROLE WITH LOGIN PASSWORD '$APP_PASS';"
  cat "$DUMP_FILE"
} > "${DUMP_FILE}.tmp" && mv "${DUMP_FILE}.tmp" "$DUMP_FILE"
