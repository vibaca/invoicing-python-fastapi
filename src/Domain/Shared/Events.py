from dataclasses import dataclass


@dataclass
class InvoiceCreated:
    invoiceId: str
    customer: str
    amount: float
    status: str = "draft"


@dataclass
class InvoiceIssued:
    invoice_id: str


@dataclass
class InvoicePaid:
    invoice_id: str


@dataclass
class InvoiceCancelled:
    invoice_id: str

