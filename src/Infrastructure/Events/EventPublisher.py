import os
import json
from typing import Any
from src.Application.Ports.Events import EventPublisherPort

# In test mode we avoid connecting to RabbitMQ (which keeps tests isolated and
# avoids asynchronous shutdown noise). Tests enable `TEST_MODE=1` or set
# `DB_NAME` to a test database (endswith `_test`) which triggers noop behaviour.
TEST_MODE = os.getenv("TEST_MODE", "0") == "1"
DB_NAME = os.getenv("DB_NAME", "")

if not TEST_MODE and not DB_NAME.endswith("_test"):
    # normal runtime: lazy-import aio_pika to avoid requiring it for tests
    from aio_pika import connect_robust, Message, ExchangeType


class EventPublisher(EventPublisherPort):
    def __init__(self):
        self._test_mode = TEST_MODE or DB_NAME.endswith("_test")
        if not self._test_mode:
            self._url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbit:5672/")

    async def publish(self, routing_key: str, payload: dict[str, Any]):
        if self._test_mode:
            # no-op in tests to avoid external dependency and async connection noise
            return
        connection = await connect_robust(self._url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange("domain_events", ExchangeType.TOPIC)
            message = Message(json.dumps(payload).encode())
            await exchange.publish(message, routing_key=routing_key)

