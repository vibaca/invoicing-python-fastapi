from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from src.Domain.Invoice.Invoice import Invoice


class InvoiceRepositoryPort(ABC):
    @abstractmethod
    async def save(self, invoice: Invoice) -> Invoice:
        raise NotImplementedError

    @abstractmethod
    async def get(self, invoice_id: str) -> Optional[Invoice]:
        raise NotImplementedError

    async def list_all(self) -> list[Invoice]:
        """Return all invoices.

        Default implementation raises NotImplementedError so test doubles
        don't need to implement it unless they use the method.
        """
        raise NotImplementedError

