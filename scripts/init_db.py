import asyncio
import logging
import os
import sys
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.Infrastructure.Database.Db import init_db, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main(db_name: str = None):
    if db_name:
        os.environ["DB_NAME"] = db_name
        logger.info(f"Initializing database: {db_name}")
    
    await init_db()
    
    try:
        await engine.dispose()
    except Exception as e:
        logger.error(f"Error disposing engine: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="Database name to initialize")
    args = parser.parse_args()
    
    asyncio.run(main(args.db))