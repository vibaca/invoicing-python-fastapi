import pytest
from uuid import uuid4

from src.Application.Commands.UpdateItem import updateInvoiceItemHandler
from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Application.Commands.DeleteItem import deleteInvoiceItemHandler
from src.Domain.ValueObject.InvoiceId import InvoiceId
from src.Domain.Shared.ValueObject.Money import Money
from src.Domain.ValueObject.InvoiceNumber import InvoiceNumber
from src.Domain.Invoice.Invoice import Invoice
from src.Domain.ValueObject.InvoiceItem import InvoiceItem


class FakeRepo(InvoiceRepositoryPort):
    def __init__(self):
        self.store = {}

    async def save(self, invoice: Invoice) -> Invoice:
        self.store[str(invoice.id.value)] = invoice
        return invoice

    async def get(self, invoice_id: str) -> Invoice | None:
        return self.store.get(invoice_id)


@pytest.mark.asyncio
async def test_update_and_delete_item_handlers():
    repo = FakeRepo()
    inv = Invoice(id=InvoiceId(uuid4()), customer="C", amount=Money(0.0), invoiceNumber=InvoiceNumber("INV-300"), items=[])
    # add an item directly
    item = InvoiceItem(product_id="P1", description="X", quantity=1, unit_price=Money(5.0))
    inv.add_item(item)
    await repo.save(inv)

    # update quantity
    updated = await updateInvoiceItemHandler(str(inv.id.value), "P1", 3, repo=repo)
    assert len(updated.items) == 1
    assert updated.amount.value == 15.0

    # delete item
    updated2 = await deleteInvoiceItemHandler(str(inv.id.value), "P1", repo=repo)
    assert len(updated2.items) == 0
    assert updated2.amount.value == 0.0


@pytest.mark.asyncio
async def test_update_item_not_allowed_when_not_draft():
    repo = FakeRepo()
    inv = Invoice(id=InvoiceId(uuid4()), customer="C", amount=Money(0.0), invoiceNumber=InvoiceNumber("INV-301"), items=[], status=__import__('src.Domain.ValueObject.InvoiceStatus', fromlist=['InvoiceStatus']).InvoiceStatus('issued'))
    item = InvoiceItem(product_id="P1", description="X", quantity=1, unit_price=Money(5.0))
    inv.items.append(item)
    await repo.save(inv)

    with pytest.raises(ValueError):
        await updateInvoiceItemHandler(str(inv.id.value), "P1", 2, repo=repo)

    with pytest.raises(ValueError):
        await deleteInvoiceItemHandler(str(inv.id.value), "P1", repo=repo)
