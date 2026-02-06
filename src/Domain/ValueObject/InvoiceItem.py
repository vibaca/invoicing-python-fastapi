from dataclasses import dataclass
from typing import Dict, Any
from src.Domain.Shared.ValueObject.Money import Money


@dataclass
class InvoiceItem:
    product_id: str
    description: str
    quantity: int
    unit_price: Money

    def __post_init__(self):
        if not isinstance(self.unit_price, Money):
            raise TypeError('unit_price must be a Money instance')

    def to_primitive(self) -> Dict[str, Any]:
        # Emit camelCase keys for external consumers (API/JSON).
        return {
            "productId": self.product_id,
            "description": self.description,
            "quantity": self.quantity,
            "unitPrice": self.unit_price.to_primitive(),
        }

    @classmethod
    def from_primitive(cls, data: Dict[str, Any]):
        # Accept both snake_case and camelCase keys to be tolerant when reading
        # persisted JSON or inputs created by older code.
        product_id = data.get("product_id") or data.get("productId") or ""
        description = data.get("description", "")
        quantity = int(data.get("quantity") or 0)
        # unit price may be present as number under snake or camel keys
        unit_price_val = data.get("unit_price") or data.get("unitPrice") or 0.0
        unit_price = Money(float(unit_price_val))
        return cls(
            product_id=product_id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
        )

