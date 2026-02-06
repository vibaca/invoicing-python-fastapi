import pytest
from uuid import uuid4

from src.Application.Commands.AddItem import addInvoiceItemHandler
from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Domain.ValueObject.InvoiceId import InvoiceId
from src.Domain.Shared.ValueObject.Money import Money
from src.Domain.ValueObject.InvoiceNumber import InvoiceNumber
from src.Domain.Invoice.Invoice import Invoice


class FakeRepo(InvoiceRepositoryPort):
    def __init__(self):
        self.store = {}

    async def save(self, invoice: Invoice) -> Invoice:
        self.store[str(invoice.id.value)] = invoice
        return invoice

    async def get(self, invoice_id: str) -> Invoice | None:
        return self.store.get(invoice_id)


@pytest.mark.asyncio
async def test_add_item_handler():
    repo = FakeRepo()
    inv = Invoice(id=InvoiceId(uuid4()), customer="C", amount=Money(0.0), invoiceNumber=InvoiceNumber("INV-200"), items=[])
    await repo.save(inv)
    updated = await addInvoiceItemHandler(str(inv.id.value), "P1", "Prod 1", 2, 5.0, repo=repo)
    assert len(updated.items) == 1
    assert updated.amount.value == 10.0
