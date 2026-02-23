#!/bin/bash
set -euo pipefail

# Create development and test databases if they don't exist.
# This script runs during initialisation as the `postgres` user.

createdb_if_missing() {
  DBNAME="$1"
  exists=$(psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DBNAME}'")
  if [ "${exists}" = "1" ]; then
    echo "Database ${DBNAME} already exists, skipping"
  else
    echo "Creating database ${DBNAME}..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -c "CREATE DATABASE \"${DBNAME}\";"
  fi
}

createdb_if_missing invoicing_dev
createdb_if_missing invoicing_test
