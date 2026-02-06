from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Application.Ports.Events import EventPublisherPort
from typing import Optional
from src.Domain.Invoice.Invoice import Invoice


async def issueInvoiceHandler(invoice_id: str, repo: Optional[InvoiceRepositoryPort] = None, publisher: Optional[EventPublisherPort] = None) -> Invoice:
    if repo is None:
        raise RuntimeError("Repository dependency not provided")
    invoice = await repo.get(invoice_id)
    if invoice is None:
        raise ValueError("Invoice not found")
    invoice.issue()
    updated = await repo.save(invoice)
    if publisher is None:
        raise RuntimeError("Event publisher dependency not provided")
    await publisher.publish("invoice.issued", {"invoice_id": str(updated.id.value), "status": updated.status.value})
    return updated
