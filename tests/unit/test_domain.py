from src.Domain.Invoice.Invoice import Invoice


def test_invoice_dataclass():
    from src.Domain.Shared.ValueObject.Money import Money
    from src.Domain.ValueObject.InvoiceId import InvoiceId
    from src.Domain.ValueObject.InvoiceNumber import InvoiceNumber
    from uuid import uuid4

    inv = Invoice(id=InvoiceId(uuid4()), customer="Bob", amount=Money(42.5), invoiceNumber=InvoiceNumber("INV-TEST"))
    assert inv.customer == "Bob"
    assert inv.amount.value == 42.5
    assert inv.status.value == "draft"
    assert inv.invoiceNumber.value == "INV-TEST"
