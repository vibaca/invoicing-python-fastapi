from src.Domain.ValueObject.InvoiceItem import InvoiceItem
from src.Domain.Shared.ValueObject.Money import Money
from uuid import uuid4


def test_invoice_item_validation():
    item = InvoiceItem(product_id="P1", description="Test product", quantity=2, unit_price=Money(10.0))
    assert item.product_id == "P1"
    assert item.unit_price.value == 10.0


def test_invoice_amount_consistency():
    from src.Domain.Invoice.Invoice import Invoice
    from src.Domain.ValueObject.InvoiceNumber import InvoiceNumber
    from src.Domain.ValueObject.InvoiceId import InvoiceId

    items = [InvoiceItem(product_id="P1", description="A", quantity=2, unit_price=Money(5.0)), InvoiceItem(product_id="P2", description="B", quantity=1, unit_price=Money(10.0))]
    inv = Invoice(id=InvoiceId(uuid4()), customer="C", amount=Money(0.0), invoiceNumber=InvoiceNumber("INV-100"), items=items)
    # amount should be set to sum(items)
    assert inv.amount.value == 20.0
