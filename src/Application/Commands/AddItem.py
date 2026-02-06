from src.Domain.ValueObject.InvoiceItem import InvoiceItem
from src.Domain.Shared.ValueObject.Money import Money
from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Application.Ports.Events import EventPublisherPort
from typing import Optional
from src.Domain.Invoice.Invoice import Invoice


async def addInvoiceItemHandler(invoice_id: str, product_id: str, description: str, quantity: int, unit_price: float, repo: Optional[InvoiceRepositoryPort] = None, publisher: Optional[EventPublisherPort] = None) -> Invoice:
    if repo is None:
        raise RuntimeError("Repository dependency not provided")
    invoice = await repo.get(invoice_id)
    if invoice is None:
        raise ValueError("Invoice not found")
    item = InvoiceItem(product_id=product_id, description=description, quantity=quantity, unit_price=Money(unit_price))
    invoice.add_item(item)
    updated = await repo.save(invoice)
    if publisher is not None:
        await publisher.publish("invoice.item.added", {"invoice_id": str(updated.id.value), "items_count": len(updated.items)})
    return updated
