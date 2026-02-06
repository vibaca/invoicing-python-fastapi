import pytest

from src.Application.Commands.CreateInvoice import createInvoiceHandler
from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Application.Ports.Events import EventPublisherPort
from src.Domain.Invoice.Invoice import Invoice


class FakeRepo(InvoiceRepositoryPort):
    def __init__(self):
        self.saved = None

    async def save(self, invoice: Invoice) -> Invoice:
        self.saved = invoice
        return invoice

    async def get(self, invoice_id: str) -> Invoice | None:
        if self.saved and str(self.saved.id.value) == invoice_id:
            return self.saved
        return None


class FakePublisher(EventPublisherPort):
    def __init__(self):
        self.published = []

    async def publish(self, topic: str, payload: dict):
        self.published.append((topic, payload))


@pytest.mark.asyncio
async def test_create_invoice_publishes_event_and_saves():
    repo = FakeRepo()
    pub = FakePublisher()
    invoice = await createInvoiceHandler("Tester", "INV-999", 12.5, repo=repo, publisher=pub)
    assert repo.saved is not None
    assert invoice.customer == "Tester"
    assert len(pub.published) == 1
    topic, payload = pub.published[0]
    assert topic == "invoice.created"
    assert payload.get("invoice_id") is not None
