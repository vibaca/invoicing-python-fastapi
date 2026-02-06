from src.Domain.ValueObject.InvoiceItem import InvoiceItem
from src.Domain.Shared.ValueObject.Money import Money


def test_invoice_item_to_primitive_emits_camelcase():
    item = InvoiceItem(product_id="P1", description="Prod", quantity=2, unit_price=Money(5.5))
    prim = item.to_primitive()
    assert "productId" in prim
    assert "unitPrice" in prim
    assert prim["productId"] == "P1"
    assert prim["unitPrice"] == 5.5


def test_invoice_item_from_primitive_accepts_both_formats():
    # camelCase input
    data_camel = {"productId": "PX", "description": "X", "quantity": 1, "unitPrice": 2.0}
    it1 = InvoiceItem.from_primitive(data_camel)
    assert it1.product_id == "PX"
    assert it1.unit_price.value == 2.0

    # snake_case input
    data_snake = {"product_id": "PY", "description": "Y", "quantity": 3, "unit_price": 4.5}
    it2 = InvoiceItem.from_primitive(data_snake)
    assert it2.product_id == "PY"
    assert it2.unit_price.value == 4.5
