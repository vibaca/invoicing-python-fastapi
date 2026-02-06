from src.Application.Ports.Repositories import InvoiceRepositoryPort
from typing import Optional
from src.Domain.Invoice.Invoice import Invoice


async def getInvoiceHandler(invoice_id: str, repo: Optional[InvoiceRepositoryPort] = None) -> Invoice | None:
    if repo is None:
        raise RuntimeError("Repository dependency not provided")
    return await repo.get(invoice_id)
