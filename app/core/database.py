from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global database instance
_db: AsyncIOMotorDatabase = None


async def connect_db():
    """Connect to MongoDB."""
    global _db
    try:
        client = AsyncIOMotorClient(settings.mongo_url)
        # Test connection
        await client.admin.command('ping')
        _db = client[settings.mongo_db]
        logger.info(f"Connected to MongoDB: {settings.mongo_db}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def disconnect_db():
    """Disconnect from MongoDB."""
    global _db
    try:
        if _db:
            client = _db.client
            client.close()
            _db = None
            logger.info("Disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Error disconnecting from MongoDB: {e}")


def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db
