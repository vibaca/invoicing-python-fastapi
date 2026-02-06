from dataclasses import dataclass


@dataclass(frozen=True)
class InvoiceStatus:
    value: str

    ALLOWED = {"draft", "issued", "paid", "cancelled"}

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError('InvoiceStatus must be a string')
        if value not in self.ALLOWED:
            raise ValueError(f"Invalid invoice status '{value}'")
        object.__setattr__(self, 'value', value)

    def to_primitive(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

