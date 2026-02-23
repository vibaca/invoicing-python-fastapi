import os
import asyncio
import logging
import warnings
from typing import Any
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped
from sqlalchemy import Column, String, Float, DateTime, func
from sqlalchemy.pool import NullPool
import atexit
# Suppress SQLAlchemy SAWarning about async DB connection objects being
# garbage-collected after the event loop is closed; best practice is to
# explicitly close sessions and dispose the engine, but tests sometimes
# terminate the loop early which triggers these warnings. Ignore them to
# keep test output clean.
from sqlalchemy.exc import SAWarning
warnings.filterwarnings("ignore", category=SAWarning)
# OperationalError is handled via generic exceptions in retry loop

# Build DATABASE_URL from environment variables so we can switch dev/test easily
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
# default to the development database
DB_NAME = os.getenv("DB_NAME", "invoicing_dev")
TEST_MODE = os.getenv("TEST_MODE", "0") == "1" or DB_NAME.endswith("_test")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# Create the async engine for Postgres (asyncpg).
# When running tests prefer NullPool to avoid pooled connection shutdown
# races that can emit un-awaited coroutine warnings during teardown.
from typing import Dict, TYPE_CHECKING

engine_kwargs: Dict[str, Any] = {"echo": False}
if TEST_MODE:
    engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
# sessionmaker is generic in stubs; annotate for mypy
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore

# Use a runtime declarative base; provide a typing-only `Base` class when
# type-checking so mypy accepts it as a valid base class for ORM models.
if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeMeta
    from sqlalchemy import MetaData

    class Base(metaclass=DeclarativeMeta):
        metadata: MetaData
else:
    Base = declarative_base()


class InvoiceModel(Base):
    __tablename__ = "invoices"
    id: Mapped[str] = Column(String(36), primary_key=True, index=True)  # type: ignore[assignment]
    customer: Mapped[str] = Column(String(255), nullable=False)  # type: ignore[assignment]
    amount: Mapped[float] = Column(Float, nullable=False)  # type: ignore[assignment]
    status: Mapped[str] = Column(String(50), nullable=False, server_default="draft")  # type: ignore[assignment]
    invoice_number: Mapped[str] = Column(String(64), nullable=False, unique=True)  # type: ignore[assignment]
    items: Mapped[str | None] = Column(String(2000), nullable=True)  # type: ignore[assignment]
    created_at: Mapped[datetime | None] = Column(DateTime, server_default=func.now())  # type: ignore[assignment]


async def init_db(retries: int = 12, delay: float = 2.0):
    """Create tables, retrying until the database is available.

    Retries `retries` times with `delay` seconds between attempts (exponential
    backoff applied). This prevents the application from exiting when Postgres
    is still starting inside Docker.
    """
    attempt = 0
    logger = logging.getLogger("invoicing.db")
    while True:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created (init_db succeeded)")
            return
        except Exception as exc:
            # OperationalError is common when DB is not ready. Retry for other
            # transient errors as well, but stop after the retry limit.
            attempt += 1
            logger.warning("init_db attempt %d failed: %s", attempt, exc)
            if attempt > retries:
                logger.error("init_db failed after %d attempts", attempt)
                raise
            wait = delay * (2 ** (attempt - 1)) if attempt > 1 else delay
            logger.info("Waiting %s seconds before retrying init_db (attempt %d)", wait, attempt + 1)
            await asyncio.sleep(wait)


# best-effort: dispose sync engine/pools on process exit
def _dispose_engine_at_exit():
    try:
        engine.sync_engine.dispose()
    except Exception as exc:
        logging.getLogger("invoicing.db").warning("dispose at exit failed: %s", exc)


# Register a best-effort atexit cleanup to close connection pools when the
# Python process exits. This helps reduce SAWarnings when tests or other
# consumers close the event loop without first disposing the engine.
atexit.register(_dispose_engine_at_exit)

