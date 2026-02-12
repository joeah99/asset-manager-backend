import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env values
load_dotenv()

# Get connection string and replace async driver with sync if necessary
# e.g. postgresql+asyncpg -> postgresql+psycopg2 (or just postgresql://)
DATABASE_URL = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
if DATABASE_URL and "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS "Users" (
    "UserId" SERIAL PRIMARY KEY,
    "FullName" VARCHAR(255) NOT NULL,
    "Email" VARCHAR(255) UNIQUE NOT NULL,
    "HashedPassword" VARCHAR(255) NOT NULL,
    "Company" VARCHAR(255),
    "Username" VARCHAR(255),
    "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_ASSETS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS "Assets" (
    "AssetId" SERIAL PRIMARY KEY,
    "UserId" INTEGER NOT NULL REFERENCES "Users"("UserId"),
    "Type" VARCHAR(100),
    "ManufactureYear" INTEGER,
    "Description" TEXT,
    "ModelYear" VARCHAR(50),
    "Manufacturer" VARCHAR(100),
    "Model" VARCHAR(100),
    "PurchasePrice" DECIMAL(18, 2),
    "CreatedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "IsDeleted" BOOLEAN DEFAULT FALSE
);
"""

def init_db():
    if not DATABASE_URL:
        logger.error("POSTGRE_SQL_CONNECTIONSTRING not found.")
        return

    logger.info(f"Connecting to database (Sync)...")
    engine = create_engine(DATABASE_URL, echo=True)

    with engine.connect() as conn:
        logger.info("creating tables...")
        conn.execute(text(CREATE_USERS_TABLE_SQL))
        conn.execute(text(CREATE_ASSETS_TABLE_SQL))
        conn.commit()
        logger.info("Tables created successfully.")

if __name__ == "__main__":
    init_db()
