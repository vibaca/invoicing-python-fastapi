import asyncio
import os
import sys

# Ensure project root is on sys.path so `from src...` imports work
# Works when running the script inside containers or on Windows where PYTHONPATH
# may not be set by the environment.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.Infrastructure.Database.Db import init_db, engine

async def main():
    await init_db()
    try:
        await engine.dispose()
    except Exception:
        pass

if __name__ == "__main__":
    asyncio.run(main())
