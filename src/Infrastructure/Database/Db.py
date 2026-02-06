import os
import asyncio
import logging
import warnings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Float, DateTime, func
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
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
# default to the development database
DB_NAME = os.getenv("DB_NAME", "invoicing_dev")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class InvoiceModel(Base):
    __tablename__ = "invoices"
    id = Column(String(36), primary_key=True, index=True)
    customer = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, server_default="draft")
    invoice_number = Column(String(64), nullable=False, unique=True)
    items = Column(String(2000), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


async def init_db(retries: int = 12, delay: float = 2.0):
    """Create tables, retrying until the database is available.

    Retries `retries` times with `delay` seconds between attempts (exponential
    backoff applied). This prevents the application from exiting when MySQL
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

