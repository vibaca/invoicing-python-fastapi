from dataclasses import dataclass


@dataclass(frozen=True)
class InvoiceNumber:
    value: str

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError('InvoiceNumber must be a string')
        if not value:
            raise ValueError('InvoiceNumber cannot be empty')
        object.__setattr__(self, 'value', value)

    def to_primitive(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

