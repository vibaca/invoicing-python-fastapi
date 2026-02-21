SHELL := /bin/bash

.PHONY: ensure-env setup reset build up down logs test test-unit test-integration test-acceptance behave check-ruff check-mypy check-pylint check-bandit check-pyright verify verify-checks

reset:
	@echo "Removing local env files (except examples)..."
	@find . -maxdepth 1 -type f -name ".env*" ! -name "*.example" -print -exec rm -f {} \; || true
	@echo "Removing docker containers/volumes/images..."
	docker-compose down -v --rmi all --remove-orphans || true
	docker system prune -af || true

build:
	docker-compose build --no-cache

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Setup development environment (docker-only): create local env files from
# `.env.example` if missing, then delegate to `scripts/setup.sh`.
setup:
	@echo "Preparing environment files..."
	@# Create .env.local from example if it doesn't exist (do not overwrite)
	@if [ ! -f .env.local ]; then cp .env.example .env.local && echo "Created .env.local from .env.example"; else echo ".env.local already exists"; fi
	@# Create .env.test from example if it doesn't exist and set DB_NAME to the test DB
	@if [ ! -f .env.test ]; then \
		cp .env.example .env.test && \
		awk 'BEGIN{FS=OFS="="} /^DB_NAME=/{print "DB_NAME=invoicing_test"; next} {print}' .env.test > .env.test.tmp && \
		mv .env.test.tmp .env.test && \
		echo "Created .env.test (DB_NAME set to invoicing_test)"; \
	else echo ".env.test already exists"; fi
	@# Ensure .env/.env.local/.env.test are present before running setup
	@$(MAKE) ensure-env
	@echo "Running scripts/setup.sh (docker-only setup)..."
	sh ./scripts/setup.sh


ensure-env:
	@# Create .env.local from .env.example if missing (example as template)
	@if [ -f .env.local ]; then \
		echo ".env.local already exists"; \
	else \
		if [ -f .env.example ]; then \
			cp .env.example .env.local && echo "Created .env.local from .env.example"; \
		else \
			echo "No .env.example found; create .env.local manually" && exit 1; \
		fi; \
	fi

	@# Create .env.test from .env.example if missing, and set DB_NAME to invoicing_test
	@if [ -f .env.test ]; then \
		echo ".env.test already exists"; \
	else \
		if [ -f .env.example ]; then \
			cp .env.example .env.test && \
			awk 'BEGIN{FS=OFS="="} /^DB_NAME=/{print "DB_NAME=invoicing_test"; next} {print}' .env.test > .env.test.tmp && \
			mv .env.test.tmp .env.test && \
			echo "Created .env.test (DB_NAME set to invoicing_test)"; \
		else \
			echo "No .env.example found; create .env.test manually" && exit 1; \
		fi; \
	fi

	@# Populate .env from .env.local if missing; fallback to .env.example
	@if [ -f .env ]; then \
		echo ".env already exists"; \
	else \
		if [ -f .env.local ]; then \
			cp .env.local .env && echo "Created .env from .env.local"; \
		elif [ -f .env.example ]; then \
			cp .env.example .env && echo "Created .env from .env.example"; \
		else \
			echo "No .env.local or .env.example found; create .env manually" && exit 1; \
		fi; \
	fi


setup-no-test:
	@echo "Running scripts/setup.sh (docker-only setup) without initializing test DB..."
	INIT_TEST_DB=0 sh ./scripts/setup.sh

# Unit tests: fast, no DB required (runs pytest)
test-unit:
	docker-compose run --rm -e PYTHONPATH=/app -e DB_NAME=invoicing_test -e TEST_MODE=1 api sh -c "pip install --no-cache-dir -r requirements-dev.txt && pytest tests/unit -q"

# Integration tests: run pytest integration suite against test DB
test-integration:
	# Ensure db + rabbit are running (do not start `api`; use existing dev api)
	docker-compose up -d db rabbit
	# Wait for Postgres and recreate a fresh test DB
	@echo "Waiting for Postgres..."
	docker-compose exec -T db sh -c 'until PGPASSWORD=password psql -h 127.0.0.1 -U postgres -d postgres -c "SELECT 1" >/dev/null 2>&1; do sleep 1; done'
	# Ensure a clean test database for this test run
	docker-compose exec -T db sh -c 'PGPASSWORD=password psql -h 127.0.0.1 -U postgres -d postgres -c "DROP DATABASE IF EXISTS invoicing_test" || true'
	docker-compose exec -T db sh -c 'PGPASSWORD=password psql -h 127.0.0.1 -U postgres -d postgres -c "CREATE DATABASE invoicing_test"'
	# Run integration tests in the existing `api` container, setting TEST env
	# so the tests use `invoicing_test` DB and no-op event publishing.
	# Ensure `api` service is available and run tests accordingly.
	@echo "Ensuring api service is available..."
	# Run integration tests inside a one-off api container configured for the
	# test database to guarantee isolation from the development database.
	@echo "Running integration tests inside one-off api container (invoicing_test)..."
	docker-compose run --rm -e DB_NAME=invoicing_test -e TEST_MODE=1 -e PYTHONPATH=/app api sh -c "pip install --no-cache-dir -r requirements-dev.txt; pytest tests/integration -q"

# Acceptance tests: behave (creates/drops test DB around run)
test-acceptance:
	# Run acceptance tests (Behave) using a temporary test DB that will be removed afterwards.
	# 1) Start DB + RabbitMQ (do not start `api`; use existing dev api)
	docker-compose up -d db rabbit
	# 2) Wait for Postgres to accept connections, then ensure the test database exists
	@echo "Waiting for Postgres to become available..."
	docker-compose exec -T db sh -c 'until PGPASSWORD=password psql -h 127.0.0.1 -U postgres -d postgres -c "SELECT 1" >/dev/null 2>&1; do sleep 1; done'
	# Ensure a clean test database for acceptance tests
	docker-compose exec -T db sh -c 'PGPASSWORD=password psql -h 127.0.0.1 -U postgres -d postgres -c "DROP DATABASE IF EXISTS invoicing_test" || true'
	docker-compose exec -T db sh -c 'PGPASSWORD=password psql -h 127.0.0.1 -U postgres -d postgres -c "CREATE DATABASE invoicing_test"'
	# 3) Ensure `api` service is available and run behave accordingly.
	@echo "Ensuring api service is available..."
	# Start an api container configured for the test DB in the background (no
	# host port binding) and run behave from a one-off container that targets
	# the api container by its container name on the docker network.
	@echo "Starting api container for acceptance tests (invoicing_test)..."
	# Use a deterministic container name and delegate acceptance flow to script
	sh ./scripts/run_acceptance.sh
	# 5) Clean up: drop the test DB (do not stop dev services)
	docker-compose exec -T db sh -c 'PGPASSWORD=password psql -h 127.0.0.1 -U postgres -d postgres -c "DROP DATABASE IF EXISTS invoicing_test;"'

# Convenience target: run all test suites sequentially
test: test-unit test-integration test-acceptance

# Static analysis / linters
check-ruff:
	docker-compose run --rm -e PYTHONPATH=/app api sh -c "pip install --no-cache-dir ruff && ruff check src tests"

check-mypy:
	docker-compose run --rm -e PYTHONPATH=/app api sh -c "pip install --no-cache-dir mypy && mypy src"

check-pylint:
	docker-compose run --rm -e PYTHONPATH=/app api sh -c "pip install --no-cache-dir pylint && pylint src || true"

check-bandit:
	docker-compose run --rm -e PYTHONPATH=/app api sh -c "pip install --no-cache-dir bandit && bandit -r src"

linters-all: check-ruff check-mypy check-pylint check-bandit

verify: linters-all test
