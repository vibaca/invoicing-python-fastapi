# Invoicing API (FastAPI)

This project is a boilerplate for building a REST invoicing API with FastAPI, following DDD, Hexagonal Architecture, SOLID, CQRS, TDD, and Domain Events (RabbitMQ). The project is Dockerized and uses MySQL as the main database. Acceptance tests are provided with Behave (Python) and can be run locally or inside the existing `api` container.

Prerequisites

- Docker and docker-compose (for the usual development flow).
- Python (only required for running the app locally without Docker).

Quick start

1. Run setup (starts infra and the API):

```bash
make setup
```

2. test the project:

```bash
make test
```

3. Open the API docs and quick endpoint reference:

```bash
# After `make verify` the app should be available at http://localhost:8000/docs
open http://localhost:8000/docs
```

Running locally (development)

If you prefer to run the API without Docker for quick iteration:

```bash
# ensure PYTHONPATH includes the project src folder
export PYTHONPATH=./src
uvicorn src.Main:app --reload --port 8000
```

Run `init_db.py` if you need to create or reset the database schema used by the app (when pointing the app to a local MySQL instance):

```bash
python scripts/init_db.py
```

Endpoint quick reference (available under `/api`):

- **Create invoice**: `POST /api/invoices`
	- Body: `{ "customer": "Customer Name", "invoiceNumber": "INV-001", "amount": 0.0 }`
	- Returns: created invoice object with `id` and metadata. Creates a `draft` invoice.

- **Get invoice**: `GET /api/invoices/{invoice_id}`
	- Path: invoice UUID (or numeric id if configured).
	- Returns: invoice details including `status` and `items`.

- **Issue invoice**: `POST /api/invoices/{invoice_id}:issue`
	- Transitions invoice from `draft` → `issued` and prevents further item edits.

- **Pay invoice**: `POST /api/invoices/{invoice_id}:pay`
	- Allowed only when invoice is `issued`. Marks invoice as `paid`.

- **Cancel invoice**: `POST /api/invoices/{invoice_id}:cancel`
	- Can cancel `draft` or `issued` invoices (business rules apply).

- **Add item**: `POST /api/invoices/{invoice_id}/items`
	- Body: `{ "productId": "P1", "description": "Product", "quantity": 1, "unitPrice": 10.0 }`
	- Allowed only when invoice is `draft`.

- **Update item**: `PATCH /api/invoices/{invoice_id}/items/{product_id}`
	- Body: `{ "quantity": 2 }` (or other fields allowed by API).
	- Allowed only when invoice is `draft`.

- **Delete item**: `DELETE /api/invoices/{invoice_id}/items/{product_id}`
	- Allowed only when invoice is `draft`.

This finishes the Quick Start.

API & project reference

OpenAPI / API Docs

- Local: run `uvicorn src.Main:app --reload --port 8000` and open `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/openapi.json`.
- Docker: `docker-compose up -d db rabbit api` then open `http://localhost:8000/docs`.

Notes

- The API is mounted under the `/api` prefix (e.g. `POST /api/invoices`).
- Responses include items in camelCase (example item: `{"productId":"P1","description":"Product","quantity":1,"unitPrice":10.0}`).

Project layout (short)

- `src/` — application code (FastAPI, domain, application, infrastructure).
- `tests/` — unit and integration tests.
- `tests/acceptance/behave` — Behave features and steps.
- `Documentation/` — guides and domain notes.

Development & common commands

- Build image: `make build`
- Start dev services: `make up`
- Full verification (linters + tests): `make verify`

Environment variables

- `DB_NAME` — database name used by the app (tests default to `invoicing_test`).
- `TEST_MODE` — set to `1` when running tests inside containers (used by some scripts).
- `INIT_TEST_DB` — set to `1` to initialize or reset the test DB when running `init_db.py`.
- `PYTHONPATH` — ensure the project `src` is on `PYTHONPATH` when running scripts or tests locally.
- `API_BASE` — used by acceptance tests to point to the base host (container name or URL).

Testing

 (Optional) Run all unit tests locally:

 ```bash
 pytest -q
 ```

- Unit tests: `pytest tests/unit -q` or `make test-unit`.
- Integration tests: `make test-integration` (recreates `invoicing_test` DB and runs `pytest tests/integration`).
- Acceptance tests (Behave): `make test-acceptance` (starts a temporary test API container, runs Behave, cleans up).

Acceptance tests (behave) notes

- The `make test-acceptance` target launches a temporary API container, waits for readiness, runs `scripts/init_db.py` inside the container and then executes Behave against that instance.
- If you run Behave manually, ensure the API is reachable (default `http://localhost:8000`) and the test DB is initialized.

Troubleshooting

- If `make setup` fails while creating databases, ensure Docker is running and the MySQL service is accepting TCP connections (the scripts use `127.0.0.1` rather than a socket).
- If pytest prints SAWarning / "Event loop is closed" traces during teardown, try re-running the tests; the project disposes the SQLAlchemy engine at test teardown to avoid these warnings but intermittent GC messages can appear in some environments.

Linters and static checks

- `make check-ruff` — ruff
- `make check-mypy` — mypy
- `make check-pylint` — pylint (non-failing by design)
- `make check-bandit` — bandit

Contributing

- When adding dependencies update `requirements.txt` and `requirements-dev.txt` accordingly.
- Run linters and tests locally via the Makefile before opening a PR.

Further reading

See `Documentation/INVOICE_STATE_TRANSITIONS.md` and `Documentation/INVOICE_ITEMS.md` for domain and API details.