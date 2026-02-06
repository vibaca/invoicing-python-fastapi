from typing import Optional, List, cast
import json

from sqlalchemy import select

from src.Infrastructure.Db import AsyncSessionLocal, InvoiceModel
from src.Domain.Invoice.Invoice import Invoice
from src.Domain.Shared.ValueObject.Money import Money
from src.Domain.ValueObject.InvoiceStatus import InvoiceStatus
from src.Domain.ValueObject.InvoiceId import InvoiceId
from src.Domain.ValueObject.InvoiceNumber import InvoiceNumber
from src.Domain.ValueObject.InvoiceItem import InvoiceItem
from src.Application.Ports.Repositories import InvoiceRepositoryPort


class InvoiceRepository(InvoiceRepositoryPort):
    async def save(self, invoice: Invoice) -> Invoice:
        async with AsyncSessionLocal() as session:  # type: ignore
            # invoice.amount is Money, invoice.status is InvoiceStatus, invoice.invoiceNumber is InvoiceNumber
            id_value: str = str(invoice.id.value)
            items_json: Optional[str] = None
            if invoice.items:
                items_json = json.dumps([it.to_primitive() for it in invoice.items])
            # prepare concrete primitives for ORM model to avoid Unknown typing
            customer_val: str = str(invoice.customer)
            amount_val: float = float(invoice.amount.value)
            status_val: str = str(invoice.status.value)
            invoice_number_val: str = str(invoice.invoiceNumber.value)
            # if exists, update; otherwise create
            obj: Optional[InvoiceModel] = await session.get(InvoiceModel, id_value)
            if obj is None:
                obj = InvoiceModel()
                obj.id = id_value
                obj.customer = customer_val
                obj.amount = amount_val
                obj.status = status_val
                obj.invoice_number = invoice_number_val
                obj.items = items_json
                session.add(obj)
            else:
                obj.customer = customer_val
                obj.amount = amount_val
                obj.status = status_val
                obj.invoice_number = invoice_number_val
                obj.items = items_json
            await session.commit()
            await session.refresh(obj)
            obj = cast(InvoiceModel, obj)
            items: List[InvoiceItem] = []
            if obj.items:
                s: str = str(obj.items)
                items = [InvoiceItem.from_primitive(d) for d in json.loads(s)]
            id_val: str = str(obj.id)
            customer_val_db: str = str(obj.customer)
            amount_val_db: float = float(obj.amount)
            status_val_db: str = str(obj.status)
            invoice_number_val_db: str = str(obj.invoice_number)
            return Invoice(id=InvoiceId(id_val), customer=customer_val_db, amount=Money(amount_val_db), status=InvoiceStatus(status_val_db), invoiceNumber=InvoiceNumber(invoice_number_val_db), items=items)

    async def get(self, invoice_id: str) -> Optional[Invoice]:
        async with AsyncSessionLocal() as session:  # type: ignore
            obj: Optional[InvoiceModel] = await session.get(InvoiceModel, invoice_id)
            if obj is None:
                return None
            obj = cast(InvoiceModel, obj)
            items: List[InvoiceItem] = []
            if obj.items:
                s: str = str(obj.items)
                items = [InvoiceItem.from_primitive(d) for d in json.loads(s)]
            id_val: str = str(obj.id)
            customer_val_db: str = str(obj.customer)
            amount_val_db: float = float(obj.amount)
            status_val_db: str = str(obj.status)
            invoice_number_val_db: str = str(obj.invoice_number)
            return Invoice(id=InvoiceId(id_val), customer=customer_val_db, amount=Money(amount_val_db), status=InvoiceStatus(status_val_db), invoiceNumber=InvoiceNumber(invoice_number_val_db), items=items)

    async def list_all(self) -> List[Invoice]:
        async with AsyncSessionLocal() as session:  # type: ignore
            result = await session.execute(select(InvoiceModel))
            objs: List[InvoiceModel] = result.scalars().all()
            invoices: List[Invoice] = []
            for obj in objs:
                obj = cast(InvoiceModel, obj)
                items: List[InvoiceItem] = []
                if obj.items:
                    s: str = str(obj.items)
                    items = [InvoiceItem.from_primitive(d) for d in json.loads(s)]
                id_val: str = str(obj.id)
                customer_val_db: str = str(obj.customer)
                amount_val_db: float = float(obj.amount)
                status_val_db: str = str(obj.status)
                invoice_number_val_db: str = str(obj.invoice_number)
                invoices.append(
                    Invoice(
                        id=InvoiceId(id_val),
                        customer=customer_val_db,
                        amount=Money(amount_val_db),
                        status=InvoiceStatus(status_val_db),
                        invoiceNumber=InvoiceNumber(invoice_number_val_db),
                        items=items,
                    )
                )
            return invoices

