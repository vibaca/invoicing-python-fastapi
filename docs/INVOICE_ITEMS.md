# Invoice Items API

This document describes how to add items to an existing invoice.

Endpoint:
- `POST /api/invoices/{invoice_id}/items` — adds an item to an existing invoice.

Request body (JSON):

{
  "productId": "P1",
  "description": "Product name",
  "quantity": 2,
  "unitPrice": 10.0
}

Response:
- `200` — `{ "id": "<invoice_id>", "items_count": n, "amount": <new_total> }`
- `404` — invoice not found
- `400` — validation or business rule error

Behavior:
- The handler constructs an `InvoiceItem` VO, calls `Invoice.add_item()`, persists the invoice and recalculates the invoice amount.
- An `invoice.item.added` event is published with payload `{ "invoice_id": "...", "items_count": n }`.

- Notes
- HTTP routes are registered in `src/Infrastructure/Adapters/Http.py` and the application entrypoint is `src/Main.py`.
- Implementations live under `src/Infrastructure/Repositories` and `src/Infrastructure/Events`; shims at `src/Infrastructure/Repositories.py` and `src/Infrastructure/Events.py` re-export the concrete modules for compatibility.
 - Tests for item operations are located under `tests/` (unit and integration). Acceptance features (Behave) live in `tests/acceptance/behave`.
- The repository no longer contains `Init.py` convenience re-export files; import handlers directly from `src/Application/Commands` or `src/Application/Queries`.
 - The repository was cleaned of `__pycache__` folders and `.gitignore` added to ignore ephemeral build files.

Implementation notes
- Item-related handlers use camelCase names (for example `addInvoiceItemHandler`, `updateInvoiceItemHandler`, `deleteInvoiceItemHandler`) and rely on ports/interfaces; concrete repos/publishers are provided by the HTTP adapter using FastAPI `Depends`.

Update / Delete:
- `PATCH /api/invoices/{invoice_id}/items/{product_id}` — update the `quantity` of an item. Body: `{ "quantity": <int> }`.
- `DELETE /api/invoices/{invoice_id}/items/{product_id}` — remove an item from the invoice.

Rules:
- Both update and delete operations are allowed only when the invoice `status` is `draft`.
- Attempts to modify items when the invoice is `issued`, `paid` or `cancelled` will return a `400` (or `404` if invoice not found).

Events:
- `invoice.item.updated` with payload `{ "invoice_id": "...", "product_id": "...", "quantity": n, "amount": total }`.
- `invoice.item.removed` with payload `{ "invoice_id": "...", "product_id": "...", "items_count": n }`.
