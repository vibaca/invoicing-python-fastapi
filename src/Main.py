"""Application entrypoint and FastAPI app configuration for the Invoicing API.

This module exposes the `app` FastAPI instance used by the ASGI server.
"""

# pylint: disable=invalid-name
import logging

from fastapi import FastAPI
from src.Infrastructure.Adapters.Http import router as api_router
from src.Infrastructure.Database.Db import init_db, engine


app = FastAPI(title="Invoicing API")
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup() -> None:
    """Startup event: initialize database tables and other resources."""
    await init_db()


@app.on_event("shutdown")
async def shutdown() -> None:
    """Shutdown event: dispose the SQLAlchemy engine to close connections."""
    try:
        # dispose underlying sync engine to close connection pools
        engine.sync_engine.dispose()
    except Exception as exc:  # log instead of silencing
        logging.getLogger("invoicing.app").warning("engine.dispose() failed: %s", exc)
