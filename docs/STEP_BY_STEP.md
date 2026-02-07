# Step-by-step: Build the Invoicing FastAPI App

This guide documents the steps taken to create this project so you can reproduce it manually and learn FastAPI, DDD, Hexagonal architecture, CQRS, domain events, and Docker.

1. Initialize repository and project layout
   - Create folders: `api/`, `tests/acceptance/behave/`, `docs/`, `scripts/`.

2. Dockerize the stack
   - Add `docker-compose.yml` with services: `api`, `db` (MySQL), and `rabbit`.
   - Write an `Dockerfile` (or `api/Dockerfile`) to install Python dependencies and run `uvicorn`.

3. Define dependencies
   - Add `api/requirements.txt` with `fastapi`, `uvicorn`, `SQLAlchemy`, `alembic`, `aio_pika`, and testing libs.

4. Design DDD + Hexagonal folders
   - `src/Domain` for entities and domain events (PascalCase folders/files).
   - `src/Application` for command/query handlers (CQRS) and `Ports`.
   - `src/Infrastructure` for adapters and concrete implementations. Implementations are organized under subpackages to avoid loose files:
     - `src/Infrastructure/Database` — DB engine, models and `init_db()`.
     - `src/Infrastructure/Repositories` — concrete repository implementations.
     - `src/Infrastructure/Events` — event publisher implementation.
     - `src/Infrastructure/Adapters` — HTTP adapter and FastAPI router (`Http.py`).
   - Compatibility shims (`src/Infrastructure/Db.py`, `src/Infrastructure/Repositories.py`, `src/Infrastructure/Events.py`) re-export the new modules to maintain backwards import compatibility.

5. Implement domain logic
   - Implement `Invoice` aggregate in `src/domain/invoice.py`.
   - Define domain events (e.g., `InvoiceCreated`) in `src/domain/events.py`.

6. Implement infrastructure
   - Use SQLAlchemy async with `aiomysql` for MySQL connectivity.
   - Write repository implementations translating domain <-> DB model (implementations under `src/Infrastructure/Repositories`).
   - Implement `EventPublisher` with `aio_pika` for RabbitMQ (implementation under `src/Infrastructure/Events`).
   - Keep adapter wiring (HTTP route dependencies) in `src/Infrastructure/Adapters/Http.py` which supplies concrete ports via FastAPI `Depends`.

7. Add application handlers
   - Implement `createInvoiceHandler` and `getInvoiceHandler` in `src/Application`.
   - Use camelCase naming for handlers (e.g. `createInvoiceHandler`). Handlers should depend only on ports/interfaces and not import concrete infra implementations.
   - Perform concrete wiring in the adapters layer (FastAPI `Depends`) located in `src/Infrastructure/Adapters/Http.py` so tests can inject mocks easily.

8. Wire HTTP layer
   - Add routes in `src/Infrastructure/Adapters/Http.py` exposing REST endpoints and include the router in `src/Main.py`.
   - Provide a lowercase compatibility shim `src/main.py` that imports `app` from `src/Main.py` so runtime/tooling that expects `src.main:app` continues to work.

9. Tests (TDD)
   - Add unit tests for domain logic with `pytest` and place tests under the repository `tests/` folder.
   - Add API tests using `httpx` `AsyncClient` (tests under `tests/integration` or `tests/unit`).
   - For acceptance tests, add `tests/acceptance/behave` with `features/` and Python `behave` step implementations to run tests locally or inside the `api` container.

10. Makefile and scripts
   - Provide `Makefile` with `setup` and `reset` targets; `setup` builds and runs containers and initializes DB.
   - Add a small `scripts/setup.sh` to run DB init. Dev dependencies for behave are installed via `requirements-dev.txt` (run locally or inside the `api` container).
   - Provide a dedicated acceptance runner `scripts/run_acceptance.sh` and a `Makefile` target `make test-acceptance` that starts a test API container, waits for readiness, runs `scripts/init_db.py`, executes `behave`, and then cleans up the test DB and container.

11. Documentation and README
   - Add a top-level `README.md` with quick start and learning goals. Keep Documentation files updated to reflect the current `src/` PascalCase layout and `tests/` location.
   - After refactors, add notes about the `src/Infrastructure` subpackages and the compatibility shims so other contributors can find implementations quickly.
   - Clean up editor/build artifacts: remove `__pycache__` folders and add/update `.gitignore` to ignore bytecode, virtualenvs, and other ephemeral files.
    - The repository no longer contains `Init.py` convenience re-export files; callers should import handler symbols directly from their command/query modules.

Follow the repository to inspect the concrete implementations and run the containers.
