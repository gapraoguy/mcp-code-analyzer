"""
Initialize database tables
"""
import asyncio
import sys
from pathlib import Path


# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.database import init_db, engine
from src.core.models import *

async def main():
    """Initialize database"""
    print("Initializing database...")
    try:
        await init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())