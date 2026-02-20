#!/usr/bin/env bash
set -euo pipefail

echo "Starting dockerized setup (db + rabbit + init)..."

# Start infra services and wait for Postgres to become available
docker-compose up -d db rabbit
echo "Waiting for Postgres to become available..."
docker-compose exec -T db sh -c 'until pg_isready -U postgres; do sleep 1; done'

echo "Creating development database invoicing_dev (if missing)..."
docker-compose exec -T db sh -c 'createdb invoicing_dev -U postgres' 2>/dev/null || true

echo "Creating test database invoicing_test (if missing)..."
docker-compose exec -T db sh -c 'createdb invoicing_test -U postgres' 2>/dev/null || true

echo "Installing base requirements in api container (quiet)..."
docker-compose run --rm -e PYTHONPATH=/app api pip install --no-cache-dir -r requirements.txt >/dev/null 2>&1 || true

echo "Initializing DB schema via api container (scripts/init_db.py)..."
docker-compose run --rm -e PYTHONPATH=/app -e DB_NAME=invoicing_dev api python scripts/init_db.py

# Optionally initialize the test DB. Set INIT_TEST_DB=0 to skip this step
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