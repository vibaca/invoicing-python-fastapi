import pytest
from src.Domain.Invoice.Invoice import Invoice
from src.Domain.ValueObject.InvoiceId import InvoiceId
from src.Domain.Shared.ValueObject.Money import Money
from src.Domain.ValueObject.InvoiceNumber import InvoiceNumber
from uuid import uuid4


def make_invoice(status: str = "draft") -> Invoice:
    return Invoice(id=InvoiceId(uuid4()), customer="Alice", amount=Money(100.0), invoiceNumber=InvoiceNumber("INV-001"), status=__import__('src.Domain.ValueObject.InvoiceStatus', fromlist=['InvoiceStatus']).InvoiceStatus(status))


def test_issue_from_draft():
    inv = make_invoice("draft")
    inv.issue()
    assert inv.status.value == "issued"


def test_issue_from_non_draft_fails():
    inv = make_invoice("issued")
    with pytest.raises(ValueError):
        inv.issue()


def test_pay_from_issued():
    inv = make_invoice("issued")
    inv.pay()
    assert inv.status.value == "paid"


def test_pay_from_non_issued_fails():
    inv = make_invoice("draft")
    with pytest.raises(ValueError):
        inv.pay()


def test_cancel_from_draft():
    inv = make_invoice("draft")
    inv.cancel()
    assert inv.status.value == "cancelled"


def test_cancel_from_issued():
    inv = make_invoice("issued")
    inv.cancel()
    assert inv.status.value == "cancelled"


def test_cancel_from_paid_fails():
    inv = make_invoice("paid")
    with pytest.raises(ValueError):
        inv.cancel()
