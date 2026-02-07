# Invoice State Transitions

This document describes the allowed state transitions for `Invoice` and how to use the API endpoints.

Allowed statuses: `draft`, `issued`, `paid`, `cancelled`.

Aggregate methods:
- `issue()`: allowed only from `draft` → sets `status` to `issued`.
- `pay()`: allowed only from `issued` → sets `status` to `paid`.
- `cancel()`: allowed from `draft` or `issued` → sets `status` to `cancelled`.

API endpoints (HTTP):
- `POST /api/invoices/{invoice_id}:issue` — issue the invoice.
- `POST /api/invoices/{invoice_id}:pay` — mark invoice as paid.
- `POST /api/invoices/{invoice_id}:cancel` — cancel invoice.

Behavior:
- If the invoice is not found, endpoints return `404`.
- If the transition is invalid, endpoints return `400` with error message.
- Successful calls return JSON with `id` and new `status`.

Events published:
- `invoice.issued`, `invoice.paid`, `invoice.cancelled` with payload `{"invoice_id": "...", "status": "..."}`.

Notes
- The API is served from `src/Main.py` and routes live in `src/Infrastructure/Adapters/Http.py`.
- Database and init functions live in `src/Infrastructure/Database/Db.py` (a shim `src/Infrastructure/Db.py` re-exports it for compatibility).
- Tests for state transitions are under `tests/` (unit/integration). Acceptance tests (Behave) are under `tests/acceptance/behave`.
- The repository no longer contains `Init.py` convenience re-export files; import handlers directly from `src/Application/Commands` or `src/Application/Queries`.

Implementation notes
- Handlers for state transitions follow the camelCase convention (for example `issueInvoiceHandler`, `payInvoiceHandler`) and depend on ports. The HTTP adapter wires concrete implementations via FastAPI dependencies.
