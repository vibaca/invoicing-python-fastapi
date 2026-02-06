from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    value: float

    def __post_init__(self):
        try:
            v = float(self.value)
        except Exception:
            raise TypeError('Money value must be a number')
        object.__setattr__(self, 'value', float(v))

    def to_primitive(self) -> float:
        return float(self.value)
