from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from src.Domain.Shared.ValueObject.Money import Money
from src.Domain.ValueObject.InvoiceStatus import InvoiceStatus
from src.Domain.ValueObject.InvoiceId import InvoiceId
from src.Domain.ValueObject.InvoiceNumber import InvoiceNumber
from src.Domain.ValueObject.InvoiceItem import InvoiceItem
# InvoiceItem is used via forward-references in annotations and imported locally where needed.


@dataclass
class Invoice:
    id: InvoiceId
    customer: str
    amount: Money
    invoiceNumber: InvoiceNumber
    status: InvoiceStatus = field(default_factory=lambda: InvoiceStatus("draft"))
    items: list["InvoiceItem"] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        # Type hints enforce value types; runtime checks removed for clarity.

        # ensure amount consistency with items when items provided
        if self.items:
            expected = sum(it.quantity * it.unit_price.value for it in self.items)
            if abs(self.amount.value - expected) > 0.0001:
                # if amount differs, set amount to sum of items
                self.amount = Money(expected)

    # Domain behavior: status transitions
    def issue(self) -> None:
        """Mark the invoice as issued.

        Allowed: draft -> issued
        """
        if self.status.value != "draft":
            raise ValueError(f"Invoice cannot be issued from status '{self.status.value}'")
        self.status = InvoiceStatus("issued")

    def pay(self) -> None:
        """Mark the invoice as paid.

        Allowed: issued -> paid
        """
        if self.status.value != "issued":
            raise ValueError(f"Invoice cannot be paid from status '{self.status.value}'")
        self.status = InvoiceStatus("paid")

    def cancel(self) -> None:
        """Cancel the invoice.

        Allowed: draft|issued -> cancelled
        """
        if self.status.value not in ("draft", "issued"):
            raise ValueError(f"Invoice cannot be cancelled from status '{self.status.value}'")
        self.status = InvoiceStatus("cancelled")

    def add_item(self, item: "InvoiceItem") -> None:
        """Add an InvoiceItem to the invoice and update the amount to match items total."""
        self.items.append(item)
        total = sum(it.quantity * it.unit_price.value for it in self.items)
        self.amount = Money(total)

    def update_item_quantity(self, product_id: str, quantity: int) -> None:
        """Update the quantity of an existing item. Allowed only in draft state."""
        if self.status.value != "draft":
            raise ValueError("Can only modify items when invoice is in draft status")
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        
        for idx, it in enumerate(self.items):
            if it.product_id == product_id:
                # replace item with new quantity
                new_item = InvoiceItem(product_id=it.product_id, description=it.description, quantity=quantity, unit_price=it.unit_price)
                self.items[idx] = new_item
                total = sum(i.quantity * i.unit_price.value for i in self.items)
                self.amount = Money(total)
                return
        raise ValueError("Item not found")

    def remove_item(self, product_id: str) -> None:
        """Remove an item by product_id. Allowed only in draft state."""
        if self.status.value != "draft":
            raise ValueError("Can only remove items when invoice is in draft status")
        for idx, it in enumerate(self.items):
            if it.product_id == product_id:
                self.items.pop(idx)
                total = sum(i.quantity * i.unit_price.value for i in self.items)
                self.amount = Money(total)
                return
        raise ValueError("Item not found")
