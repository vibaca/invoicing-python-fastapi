SHELL := /bin/bash

.PHONY: setup reset build up down logs test test-unit test-integration test-acceptance behave check-ruff check-mypy check-pylint check-bandit verify verify-checks

reset:
	docker-compose down -v --rmi all --remove-orphans || true
	docker system prune -af || true
	@echo "Removing local env files: .env .env.test"
	-rm -f .env .env.test

build:
	docker-compose build --no-cache

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Setup development environment (docker-only): delegate to `scripts/setup.sh`
setup:
	@echo "Generating .env and .env.test from .env.example..."
	python3 ./scripts/generate_envs.py
	@echo "Running scripts/setup.sh (docker-only setup)..."
	sh ./scripts/setup.sh
	
setup-no-test:
	@echo "Running scripts/setup.sh (docker-only setup) without initializing test DB..."
	INIT_TEST_DB=0 sh ./scripts/setup.sh

# Unit tests: fast, no DB required (runs pytest)
test-unit:
	docker-compose run --rm -e DB_NAME=invoicing_test -e TEST_MODE=1 -w /app api pytest tests/unit -q --exitfirst

# Integration tests: run pytest integration suite against test DB
test-integration:
	# Ensure db + rabbit are running (do not start `api`; use existing dev api)
	docker-compose up -d db rabbit
	# Wait for Postgres and recreate a fresh test DB
	@echo "Waiting for Postgres..."
	docker-compose exec -T db sh -c 'until pg_isready -U postgres; do sleep 1; done'
	# Ensure a clean test database for this test run
	docker-compose exec -T db sh -c 'dropdb --if-exists invoicing_test -U postgres'
	docker-compose exec -T db sh -c 'createdb invoicing_test -U postgres'
	# Run integration tests in the existing `api` container, setting TEST env
	# so the tests use `invoicing_test` DB and no-op event publishing.
	# Ensure `api` service is available and run tests accordingly.
	@echo "Ensuring api service is available..."
	# Run integration tests inside a one-off api container configured for the
	# test database to guarantee isolation from the development database.
	@echo "Running integration tests inside one-off api container (invoicing_test)..."
	docker-compose run --rm -e DB_NAME=invoicing_test -e TEST_MODE=1 -w /app api pytest tests/integration -q --exitfirst

# Acceptance tests: behave (creates/drops test DB around run)
test-acceptance:
	# Start dependencies
	docker-compose up -d db rabbit
	
	# Wait for Postgres
	@echo "Waiting for Postgres..."
	docker-compose exec -T db sh -c 'until pg_isready -U postgres; do sleep 1; done'
	
	# Create clean test database
	docker-compose exec -T db sh -c 'dropdb --if-exists invoicing_test -U postgres'
	docker-compose exec -T db sh -c 'createdb invoicing_test -U postgres'
	
	# Run database migrations on test DB
	docker-compose run --rm -e DB_NAME=invoicing_test api python scripts/init_db.py
	
	# Start API container for tests (background, no port binding)
	docker-compose run -d --name invoicing_test_api \
		-e DB_NAME=invoicing_test \
		-e TEST_MODE=1 \
		api
	
	# Wait for API to be ready
	@echo "Waiting for API..."
	@until docker exec invoicing_test_api curl -s http://localhost:8000/docs >/dev/null 2>&1; do \
		sleep 1; \
	done
	
	# Run behave tests
	docker-compose run --rm \
		-e DB_NAME=invoicing_test \
		-e TEST_MODE=1 \
		-e API_BASE=http://invoicing_test_api:8000/api \
		-w /app \
		api behave tests/acceptance/behave/features
	
	# Cleanup
	@echo "Cleaning up..."
	-docker rm -f invoicing_test_api 2>/dev/null
	docker-compose exec -T db sh -c 'dropdb --if-exists invoicing_test -U postgres'

# Convenience target: run all test suites sequentially
test: test-unit test-integration test-acceptance
# Static analysis / linters
check-ruff:
	docker-compose run --rm api ruff check src tests
check-mypy:
	docker-compose run --rm api mypy src
check-pylint:
	docker-compose run --rm api pylint src || true
check-bandit:
	docker-compose run --rm api bandit -r src

linters-all: check-ruff check-mypy check-pylint check-bandit

verify: linters-all test