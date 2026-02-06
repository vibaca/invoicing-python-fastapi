#!/usr/bin/env bash
set -eu

# This script performs the acceptance test flow previously embedded
# in the Makefile. Keeping it here avoids complex quoting issues.

TEST_API_NAME=invoicing_test_api

docker rm -f "$TEST_API_NAME" >/dev/null 2>&1 || true

docker-compose run -d --name "$TEST_API_NAME" -e DB_NAME=invoicing_test -e TEST_MODE=1 -e PYTHONPATH=/app api >/dev/null

echo "Started api container $TEST_API_NAME"

echo "Waiting for api to become available..."
# Wait until the container is up and the service responds on /docs
until docker exec -i "$TEST_API_NAME" sh -c 'curl -sS -f http://127.0.0.1:8000/docs >/dev/null 2>&1'; do
    sleep 1
done

# Ensure the DB schema exists
docker-compose run --rm -e DB_NAME=invoicing_test -e TEST_MODE=1 -e PYTHONPATH=/app api python scripts/init_db.py

# Run behave pointing at the test api container
docker-compose run --rm -e DB_NAME=invoicing_test -e TEST_MODE=1 -e API_BASE=http://$TEST_API_NAME:8000/api -e PYTHONPATH=/app api sh -c "pip install --no-cache-dir -r requirements-dev.txt; behave -f progress tests/acceptance/behave/features"

# Clean up
docker rm -f "$TEST_API_NAME" || true

docker-compose exec -T db mysql -u root -ppassword -e "DROP DATABASE IF EXISTS invoicing_test;"
