from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Application.Ports.Events import EventPublisherPort
from typing import Optional
from src.Domain.Invoice.Invoice import Invoice


async def updateInvoiceItemHandler(invoice_id: str, product_id: str, quantity: int, repo: Optional[InvoiceRepositoryPort] = None, publisher: Optional[EventPublisherPort] = None) -> Invoice:
    if repo is None:
        raise RuntimeError("Repository dependency not provided")
    invoice = await repo.get(invoice_id)
    if invoice is None:
        raise ValueError("Invoice not found")
    invoice.update_item_quantity(product_id, quantity)
    updated = await repo.save(invoice)
    if publisher is not None:
        await publisher.publish("invoice.item.updated", {"invoice_id": str(updated.id.value), "product_id": product_id, "quantity": quantity, "amount": updated.amount.value})
    return updated
