from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class EventPublisherPort(ABC):
    @abstractmethod
    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError

