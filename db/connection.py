from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()

_engine = None
_AsyncSessionLocal = None

def _get_engine():
    global _engine, _AsyncSessionLocal
    if _engine is None:
        DATABASE_URL = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
        if not DATABASE_URL:
            raise RuntimeError("POSTGRE_SQL_CONNECTIONSTRING environment variable is not set.")
        if DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        _engine = create_async_engine(DATABASE_URL, echo=False)
        _AsyncSessionLocal = sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)
        logger.info("Database engine initialized.")
    return _engine, _AsyncSessionLocal

async def get_db():
    _, AsyncSessionLocal = _get_engine()
    async with AsyncSessionLocal() as session:
        yield session

