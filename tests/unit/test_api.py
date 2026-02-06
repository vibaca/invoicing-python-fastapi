import pytest
try:
    from httpx import AsyncClient
    _HAS_HTTPX = True
except Exception:
    _HAS_HTTPX = False
from src.Main import app
from src.Infrastructure.Adapters.Http import getRepository, getPublisher


class InMemoryRepo:
    def __init__(self):
        self.store = {}

    async def save(self, invoice):
        self.store[str(invoice.id.value)] = invoice
        return invoice

    async def get(self, invoice_id):
        return self.store.get(invoice_id)


class DummyPublisher:
    async def publish(self, key, payload):
        return None


@pytest.mark.asyncio
@pytest.mark.skipif(not _HAS_HTTPX, reason="httpx/httpcore import failed (incompatible Python)")
async def test_create_and_get_invoice():
    from uuid import uuid4
    # use an in-memory repo and dummy publisher to avoid DB in unit test
    app.dependency_overrides[getRepository] = lambda: InMemoryRepo()
    app.dependency_overrides[getPublisher] = lambda: DummyPublisher()

    # persistent client supporting older and newer httpx
    try:
        client = AsyncClient(app=app, base_url="http://test")
    except TypeError:
        from httpx import ASGITransport
        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    await client.__aenter__()
    try:
        invoice_number = f"INV-{uuid4().hex[:8]}"
        resp = await client.post("/api/invoices", json={"customer": "Test", "amount": 12.5, "invoiceNumber": invoice_number})
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        # ensure id looks like a UUID string
        assert isinstance(data.get("id"), str) and len(data.get("id")) > 0
        assert data.get("status") == "draft"
        assert data.get("invoiceNumber") == invoice_number
    finally:
        await client.__aexit__(None, None, None)
