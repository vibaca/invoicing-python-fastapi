from src.Domain.Invoice.Invoice import Invoice
from src.Domain.Shared.ValueObject.Money import Money
from src.Domain.ValueObject.InvoiceId import InvoiceId
from src.Domain.ValueObject.InvoiceNumber import InvoiceNumber
from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Application.Ports.Events import EventPublisherPort
from typing import Optional
from uuid import uuid4


async def createInvoiceHandler(customer: str, invoice_number: str, amount: Optional[float] = 0.0, repo: Optional[InvoiceRepositoryPort] = None, publisher: Optional[EventPublisherPort] = None) -> Invoice:
    if repo is None:
        raise RuntimeError("Repository dependency not provided")
    # default amount to 0.0 when not provided
    amount_vo = Money(amount if amount is not None else 0.0)
    id_vo = InvoiceId(uuid4())
    invoice_number_vo = InvoiceNumber(invoice_number)
    invoice = Invoice(id=id_vo, customer=customer, amount=amount_vo, invoiceNumber=invoice_number_vo)
    created = await repo.save(invoice)
    if publisher is None:
        raise RuntimeError("Event publisher dependency not provided")
    invoice_id_value = created.id.value
    await publisher.publish("invoice.created", {"invoice_id": str(invoice_id_value), "customer": created.customer, "amount": created.amount.value, "status": created.status.value, "invoiceNumber": created.invoiceNumber.value})
    return created
