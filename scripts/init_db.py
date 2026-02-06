import asyncio
from src.Infrastructure.Database.Db import init_db, engine

async def main():
    await init_db()
    try:
        await engine.dispose()
    except Exception:
        pass

if __name__ == "__main__":
    asyncio.run(main())
