from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.Application.Commands.CreateInvoice import createInvoiceHandler
from src.Application.Queries.GetInvoice import getInvoiceHandler
from src.Application.Commands.IssueInvoice import issueInvoiceHandler
from src.Application.Commands.PayInvoice import payInvoiceHandler
from src.Application.Commands.CancelInvoice import cancelInvoiceHandler
from src.Application.Commands.AddItem import addInvoiceItemHandler
from src.Application.Commands.UpdateItem import updateInvoiceItemHandler
from src.Application.Commands.DeleteItem import deleteInvoiceItemHandler
from src.Infrastructure.Repositories.InvoiceRepository import InvoiceRepository
from src.Infrastructure.Events.EventPublisher import EventPublisher
from src.Application.Ports.Repositories import InvoiceRepositoryPort
from src.Application.Ports.Events import EventPublisherPort


def getRepository():
    return InvoiceRepository()


def getPublisher():
    return EventPublisher()

router = APIRouter()


class CreateInvoiceDTO(BaseModel):
    customer: str
    invoiceNumber: str


class CreateInvoiceItemDTO(BaseModel):
    productId: str
    description: str
    quantity: int
    unitPrice: float


class UpdateInvoiceItemDTO(BaseModel):
    quantity: int



class InvoiceItemResponse(BaseModel):
    productId: str
    description: str
    quantity: int
    unitPrice: float

    class Config:
        schema_extra = {
            "example": {"productId": "P1", "description": "Product", "quantity": 1, "unitPrice": 10.0}
        }


class InvoiceResponse(BaseModel):
    id: Optional[str]
    customer: str
    amount: float
    status: str
    invoiceNumber: str
    items: List[InvoiceItemResponse] = []

    class Config:
        schema_extra = {
            "example": {
                "id": "uuid", "customer": "ACME", "amount": 100.0, "status": "draft", "invoiceNumber": "INV-1", "items": []
            }
        }


@router.post("/invoices", response_model=InvoiceResponse)
async def createInvoice(dto: CreateInvoiceDTO, repo: InvoiceRepositoryPort = Depends(getRepository), publisher: EventPublisherPort = Depends(getPublisher)) -> InvoiceResponse:
    try:
        # amount is optional and defaults to 0.0 on creation
        invoice = await createInvoiceHandler(dto.customer, dto.invoiceNumber, 0.0, repo=repo, publisher=publisher)
        id_value = str(invoice.id.value) if invoice.id is not None else None
        resp = InvoiceResponse(
            id=id_value,
            customer=invoice.customer,
            amount=invoice.amount.value,
            status=invoice.status.value,
            invoiceNumber=invoice.invoiceNumber.value,
                items=[
                    InvoiceItemResponse(
                        productId=str(it.get("product_id") or it.get("productId") or ""),
                        description=str(it.get("description") or ""),
                        quantity=int(it.get("quantity") or 0),
                        unitPrice=float(it.get("unit_price") or it.get("unitPrice") or 0.0),
                    )
                    for it in ([it.to_primitive() for it in invoice.items] if invoice.items else [])
                ],
        )
        return resp
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def getInvoice(invoice_id: str, repo: InvoiceRepositoryPort = Depends(getRepository)) -> InvoiceResponse:
    invoice = await getInvoiceHandler(invoice_id, repo=repo)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    id_value = str(invoice.id.value) if invoice.id is not None else None
    items = [it.to_primitive() for it in invoice.items] if invoice.items else []
    resp = InvoiceResponse(
        id=id_value,
        customer=invoice.customer,
        amount=invoice.amount.value,
        status=invoice.status.value,
        invoiceNumber=invoice.invoiceNumber.value,
        items=[
            InvoiceItemResponse(
                productId=str(it.get("product_id") or it.get("productId") or ""),
                description=str(it.get("description") or ""),
                quantity=int(it.get("quantity") or 0),
                unitPrice=float(it.get("unit_price") or it.get("unitPrice") or 0.0),
            )
            for it in items
        ],
    )
    return resp


@router.get("/invoices", response_model=List[InvoiceResponse])
async def listInvoices(repo: InvoiceRepositoryPort = Depends(getRepository)) -> List[InvoiceResponse]:
    try:
        invoices = await repo.list_all()
        result: List[InvoiceResponse] = []
        for invoice in invoices:
            id_value = str(invoice.id.value) if invoice.id is not None else None
            items = [it.to_primitive() for it in invoice.items] if invoice.items else []
            resp = InvoiceResponse(
                id=id_value,
                customer=invoice.customer,
                amount=invoice.amount.value,
                status=invoice.status.value,
                invoiceNumber=invoice.invoiceNumber.value,
                items=[
                    InvoiceItemResponse(
                        productId=str(it.get("product_id") or it.get("productId") or ""),
                        description=str(it.get("description") or ""),
                        quantity=int(it.get("quantity") or 0),
                        unitPrice=float(it.get("unit_price") or it.get("unitPrice") or 0.0),
                    )
                    for it in items
                ],
            )
            result.append(resp)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoices/{invoice_id}:issue")
async def issueInvoice(invoice_id: str, repo: InvoiceRepositoryPort = Depends(getRepository), publisher: EventPublisherPort = Depends(getPublisher)):
    try:
        invoice = await issueInvoiceHandler(invoice_id, repo=repo, publisher=publisher)
        return {"id": str(invoice.id.value), "status": invoice.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/{invoice_id}:pay")
async def payInvoice(invoice_id: str, repo: InvoiceRepositoryPort = Depends(getRepository), publisher: EventPublisherPort = Depends(getPublisher)):
    try:
        invoice = await payInvoiceHandler(invoice_id, repo=repo, publisher=publisher)
        return {"id": str(invoice.id.value), "status": invoice.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/{invoice_id}:cancel")
async def cancelInvoice(invoice_id: str, repo: InvoiceRepositoryPort = Depends(getRepository), publisher: EventPublisherPort = Depends(getPublisher)):
    try:
        invoice = await cancelInvoiceHandler(invoice_id, repo=repo, publisher=publisher)
        return {"id": str(invoice.id.value), "status": invoice.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/{invoice_id}/items")
async def addInvoiceItem(invoice_id: str, dto: CreateInvoiceItemDTO, repo: InvoiceRepositoryPort = Depends(getRepository), publisher: EventPublisherPort = Depends(getPublisher)):
    try:
        invoice = await addInvoiceItemHandler(invoice_id, dto.productId, dto.description, dto.quantity, dto.unitPrice, repo=repo, publisher=publisher)
        return {"id": str(invoice.id.value), "items_count": len(invoice.items), "amount": invoice.amount.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/invoices/{invoice_id}/items/{product_id}")
async def updateInvoiceItem(invoice_id: str, product_id: str, dto: UpdateInvoiceItemDTO, repo: InvoiceRepositoryPort = Depends(getRepository), publisher: EventPublisherPort = Depends(getPublisher)):
    try:
        invoice = await updateInvoiceItemHandler(invoice_id, product_id, dto.quantity, repo=repo, publisher=publisher)
        return {"id": str(invoice.id.value), "items_count": len(invoice.items), "amount": invoice.amount.value}
    except ValueError as e:
        # invoice not found or business rule
        raise HTTPException(status_code=404 if str(e) == "Invoice not found" else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/invoices/{invoice_id}/items/{product_id}")
async def deleteInvoiceItem(invoice_id: str, product_id: str, repo: InvoiceRepositoryPort = Depends(getRepository), publisher: EventPublisherPort = Depends(getPublisher)):
    try:
        invoice = await deleteInvoiceItemHandler(invoice_id, product_id, repo=repo, publisher=publisher)
        return {"id": str(invoice.id.value), "items_count": len(invoice.items), "amount": invoice.amount.value}
    except ValueError as e:
        raise HTTPException(status_code=404 if str(e) == "Invoice not found" else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
