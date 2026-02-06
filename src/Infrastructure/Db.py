"""Compatibility shim for older imports expecting `src.Infrastructure.Db`.

Re-exports the real implementations from `src.Infrastructure.Database.Db`.
"""
from src.Infrastructure.Database.Db import AsyncSessionLocal, InvoiceModel, init_db

__all__ = ["AsyncSessionLocal", "InvoiceModel", "init_db"]
