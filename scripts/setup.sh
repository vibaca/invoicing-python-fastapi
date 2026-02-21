#!/usr/bin/env bash
set -euo pipefail

echo "Starting dockerized setup (db + rabbit + init)..."

# Start infra services and wait for Postgres to become available
docker-compose up -d db rabbit
# Use TCP (127.0.0.1) inside the container to avoid socket connection issues
echo "Waiting for Postgres to become available..."
# Use TCP (127.0.0.1) inside the container to avoid socket connection issues
docker-compose exec -T db sh -c 'until PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U postgres -d postgres -c "SELECT 1" >/dev/null 2>&1; do sleep 1; done'

echo "Creating development database invoicing_dev (if missing)..."
docker-compose exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U postgres -d postgres -c "CREATE DATABASE invoicing_dev" >/dev/null 2>&1 || true'

echo "Creating test database invoicing_test (if missing)..."
docker-compose exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U postgres -d postgres -c "CREATE DATABASE invoicing_test" >/dev/null 2>&1 || true'

echo "Installing base requirements in api container (quiet)..."
docker-compose run --rm -e PYTHONPATH=/app api pip install --no-cache-dir -r requirements.txt >/dev/null 2>&1 || true

echo "Initializing DB schema via api container (scripts/init_db.py)..."
docker-compose run --rm -e PYTHONPATH=/app -e DB_NAME=invoicing_dev api python scripts/init_db.py

# Optionally initialize the test DB. Set INIT_TEST_DB=0 to skip this step
# (useful when you want a clean development DB and don't want the test
# fixtures or initialization to touch your dev database).
if [ "${INIT_TEST_DB:-1}" = "1" ]; then
	echo "Initializing test DB schema via api container (in test mode)..."
	docker-compose run --rm -e PYTHONPATH=/app -e DB_NAME=invoicing_test -e TEST_MODE=1 api python scripts/init_db.py
else
	echo "Skipping test DB initialization (INIT_TEST_DB=0)"
fi

echo "Dev dependencies can be installed locally: pip install -r requirements-dev.txt"

echo "Starting api service (development)..."
docker-compose up -d api

echo "Setup complete"
