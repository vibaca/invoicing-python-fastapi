from dataclasses import dataclass
from typing import Union
import uuid


@dataclass(frozen=True)
class InvoiceId:
    value: uuid.UUID

    def __init__(self, value: Union[uuid.UUID, str]):
        if isinstance(value, uuid.UUID):
            object.__setattr__(self, 'value', value)
        elif isinstance(value, str):
            object.__setattr__(self, 'value', uuid.UUID(value))
        else:
            raise TypeError('InvoiceId must be constructed from uuid.UUID or str')

    @classmethod
    def generate(cls):
        return cls(uuid.uuid4())

    def to_primitive(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)
"""Compatibility shim: old lowercase module name importing PascalCase implementation."""
