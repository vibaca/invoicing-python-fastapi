import pytest
try:
    from httpx import AsyncClient
    _HAS_HTTPX = True
except Exception:
    _HAS_HTTPX = False
from src.Main import app
from uuid import uuid4
from src.Infrastructure.Database.Db import init_db


@pytest.mark.asyncio
@pytest.mark.skipif(not _HAS_HTTPX, reason="httpx/httpcore import failed (incompatible Python)")
async def test_create_and_add_item_endpoint(monkeypatch):
    # httpx dropped the `app=` shorthand in newer versions; support both forms
    # create a persistent client compatible with older and newer httpx
    try:
        client = AsyncClient(app=app, base_url="http://test")
    except TypeError:
        from httpx import ASGITransport
        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    await client.__aenter__()
    try:
        # ensure DB tables exist (startup event may not have completed in test env)
        await init_db()
        payload = {"customer": "Test", "invoiceNumber": f"INV-INT-{uuid4().hex[:8]}"}
        r = await client.post("/api/invoices", json=payload)
        assert r.status_code == 200
        data = r.json()
        invoice_id = data["id"]

        # add item
        item_payload = {"productId": "P1", "description": "Prod", "quantity": 2, "unitPrice": 5.0}
        r2 = await client.post(f"/api/invoices/{invoice_id}/items", json=item_payload)
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["items_count"] == 1
        assert d2["amount"] == 10.0
    finally:
        await client.__aexit__(None, None, None)

@pytest.mark.asyncio
@pytest.mark.skipif(not _HAS_HTTPX, reason="httpx/httpcore import failed (incompatible Python)")
async def test_get_invoices_list_includes_items():
    try:
        client = AsyncClient(app=app, base_url="http://test")
    except TypeError:
        from httpx import ASGITransport
        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    await client.__aenter__()
    try:
        await init_db()
        payload = {"customer": "ListTest", "invoiceNumber": f"INV-LIST-{uuid4().hex[:8]}"}
        r = await client.post("/api/invoices", json=payload)
        assert r.status_code == 200
        data = r.json()
        invoice_id = data["id"]

        item_payload = {"productId": "P10", "description": "Prod10", "quantity": 3, "unitPrice": 2.5}
        r2 = await client.post(f"/api/invoices/{invoice_id}/items", json=item_payload)
        assert r2.status_code == 200

        r3 = await client.get("/api/invoices")
        assert r3.status_code == 200
        invoices = r3.json()
        found = [inv for inv in invoices if inv.get("id") == invoice_id]
        assert found, "Created invoice not present in list"
        inv = found[0]
        assert "items" in inv
        assert isinstance(inv["items"], list)
        assert any(it.get("product_id") == "P10" or it.get("productId") == "P10" for it in inv["items"])
    finally:
        await client.__aexit__(None, None, None)


@pytest.mark.asyncio
@pytest.mark.skipif(not _HAS_HTTPX, reason="httpx/httpcore import failed (incompatible Python)")
async def test_get_invoice_includes_items():
    try:
        client = AsyncClient(app=app, base_url="http://test")
    except TypeError:
        from httpx import ASGITransport
        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    await client.__aenter__()
    try:
        await init_db()
        payload = {"customer": "SingleTest", "invoiceNumber": f"INV-SGL-{uuid4().hex[:8]}"}
        r = await client.post("/api/invoices", json=payload)
        assert r.status_code == 200
        data = r.json()
        invoice_id = data["id"]

        item_payload = {"productId": "PX", "description": "SingleProd", "quantity": 1, "unitPrice": 9.99}
        r2 = await client.post(f"/api/invoices/{invoice_id}/items", json=item_payload)
        assert r2.status_code == 200

        r3 = await client.get(f"/api/invoices/{invoice_id}")
        assert r3.status_code == 200
        inv = r3.json()
        assert "items" in inv
        assert isinstance(inv["items"], list)
        assert any(it.get("product_id") == "PX" or it.get("productId") == "PX" for it in inv["items"])
    finally:
        await client.__aexit__(None, None, None)
