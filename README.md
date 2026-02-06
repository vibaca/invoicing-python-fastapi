# Invoicing API (FastAPI) — Learning Project

This project is a learning scaffold for building a REST invoicing API with FastAPI, following DDD, Hexagonal Architecture, SOLID, CQRS, TDD, and Domain Events (RabbitMQ). The project is Dockerized and uses MySQL as the main database. Acceptance tests are provided with Behave (Python) and can be run locally or inside the existing `api` container.

Quick start

1. Build and run everything:

```bash
make setup
```

2. Run unit tests locally:

```bash
pytest -q
```

3. Run acceptance tests (Behave):

```bash
# Preferred: use the Makefile helper which runs behave inside a test API container
make test-acceptance

# Or run locally against a running API (install dev deps first)
docker-compose up -d db rabbit api
pip install -r requirements-dev.txt
behave -f progress tests/acceptance/behave/features
```

Project layout (current)

- `src/` — Python FastAPI application (PascalCase modules)
	- `src/Application/` — application layer (Commands, Queries, Ports)
	- `src/Domain/` — domain models and value objects
	- `src/Infrastructure/` — adapters and infra (Adapters, Db, Events, Repositories)
	- `src/Infrastructure/` — adapters and infra (Adapters, Database, Repositories, Events).
		- Implementation modules are organized under subpackages: `src/Infrastructure/Database`, `src/Infrastructure/Repositories`, `src/Infrastructure/Events`.
		- Backwards-compatible shims exist at `src/Infrastructure/Db.py`, `src/Infrastructure/Repositories.py`, `src/Infrastructure/Events.py` that re-export implementations to avoid breaking older imports.
		- A lowercase entrypoint shim `src/main.py` is provided that imports `app` from `src/Main.py` so tools can reference either `src.Main:app` or `src.main:app`.
	- `src/Main.py` — FastAPI app entrypoint (exposes `app`)
- `tests/` — unit and integration tests (moved to repository root)
- `tests/acceptance/behave` — Behave feature files and Python test setup
- `Documentation/` — step-by-step guides and domain notes

See `Documentation/STEP_BY_STEP.md` for a step-by-step guide (updated to match the current layout).

New endpoints added:

- `POST /api/invoices` — create invoice (JSON: `customer`, `invoiceNumber`) — `amount` is optional and defaults to `0.0`.
- `GET /api/invoices/{invoice_id}` — get invoice.
- `POST /api/invoices/{invoice_id}:issue` — issue invoice.
- `POST /api/invoices/{invoice_id}:pay` — pay invoice.
- `POST /api/invoices/{invoice_id}:cancel` — cancel invoice.
- `POST /api/invoices/{invoice_id}/items` — add an item to invoice (JSON: `productId`, `description`, `quantity`, `unitPrice`).

- `PATCH /api/invoices/{invoice_id}/items/{product_id}` — update item quantity (JSON: `quantity`). Allowed only when invoice is `draft`.
- `DELETE /api/invoices/{invoice_id}/items/{product_id}` — remove an item. Allowed only when invoice is `draft`.

**OpenAPI / API Docs**

- **Local (uvicorn):** ejecuta `uvicorn src.Main:app --reload --port 8000` y abre `http://localhost:8000/docs` (Swagger UI) o `http://localhost:8000/openapi.json` (JSON).
- **Docker (docker-compose):** si usas Docker, arranca los servicios y el contenedor `api`:

```bash
docker-compose up -d db rabbit api
```

Luego abre `http://localhost:8000/docs`.
- **Nota:** las rutas del API están prefijadas con `/api` (por ejemplo `POST /api/invoices`).
- **Respuesta de `items`:** las respuestas JSON de los endpoints incluyen los items en camelCase. Ejemplo de item en la respuesta:

```json
{"productId": "P1", "description": "Product", "quantity": 1, "unitPrice": 10.0}
```

CQRS note: application handlers are organized under `src/Application/Commands` and `src/Application/Queries`. Ports live in `src/Application/Ports`. A small compatibility layer (`__init__.py` re-exports) may exist in some folders for legacy imports.

Notes on naming and wiring:

- **Handler naming:** handlers use camelCase (for example `createInvoiceHandler`, `getInvoiceHandler`, `addInvoiceItemHandler`).
- **Dependency wiring:** concrete implementations (repositories, event publishers) are provided by the adapters layer using FastAPI `Depends` (see `src/Infrastructure/Adapters/Http.py`), so handlers depend only on ports/interfaces for easy testing and substitution.

- **Files & tooling:** `__pycache__` folders were removed and `.gitignore` updated to ignore bytecode files. Compatibility shims were added under `src/` to minimise runtime import changes after refactors.
- **Removed re-exports:** Convenience re-export `Init.py` files (previously present under `src/Application` and `src/Infrastructure/Adapters`) were removed — import handlers directly from their modules under `src/Application/Commands` or `src/Application/Queries` (or use `src/Application/Handlers` module exports where present).

# Test commands (local):

```bash
# run unit and integration tests locally
pytest -q

# run Behave acceptance tests (locally or inside the `api` container)
# Start infra and API
docker-compose up -d db rabbit api

# run behave from host (recommended)
pip install -r requirements-dev.txt
behave -f progress tests/acceptance/behave/features

# or run inside the existing api container:
docker-compose run --rm -e PYTHONPATH=/app api sh -c "pip install --no-cache-dir -r requirements-dev.txt && behave -f progress tests/acceptance/behave/features"

# Makefile helpers
make test-unit         # run unit tests inside api container
make test-integration  # recreate test DB and run integration tests
make test-acceptance   # run acceptance tests using scripts/run_acceptance.sh

# Linters
make check-ruff        # run ruff
make check-mypy        # run mypy
make check-pylint      # run pylint (non-failing)
make check-bandit      # run bandit
```

See `Documentation/INVOICE_STATE_TRANSITIONS.md` and `Documentation/INVOICE_ITEMS.md` for domain and API details.
