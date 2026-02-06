import pytest
from uuid import uuid4

from src.Application.Commands.IssueInvoice import issueInvoiceHandler
from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Application.Ports.Events import EventPublisherPort
from src.Application.Commands.PayInvoice import payInvoiceHandler
from src.Application.Commands.CancelInvoice import cancelInvoiceHandler
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


class FakePublisher(EventPublisherPort):
    def __init__(self):
        self.published = []

    async def publish(self, topic: str, payload: dict):
        self.published.append((topic, payload))


@pytest.mark.asyncio
async def test_issue_pay_cancel_handlers_publish_events():
    repo = FakeRepo()
    pub = FakePublisher()
    inv = Invoice(id=InvoiceId(uuid4()), customer="A", amount=Money(10.0), invoiceNumber=InvoiceNumber("INV-H1"))
    await repo.save(inv)

    issued = await issueInvoiceHandler(str(inv.id.value), repo=repo, publisher=pub)
    assert issued.status.value == "issued"
    assert pub.published[-1][0] == "invoice.issued"

    paid = await payInvoiceHandler(str(inv.id.value), repo=repo, publisher=pub)
    assert paid.status.value == "paid"
    assert pub.published[-1][0] == "invoice.paid"

    # cancel from paid should fail
    with pytest.raises(Exception):
        await cancelInvoiceHandler(str(inv.id.value), repo=repo, publisher=pub)
