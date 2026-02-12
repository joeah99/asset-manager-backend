import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env values
load_dotenv()

DATABASE_URL = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

# Core Schema SQL
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
    "BookValue" DECIMAL(18, 2) DEFAULT 0,
    "CreatedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "IsDeleted" BOOLEAN DEFAULT FALSE
);
"""

CREATE_LOANS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS "Loans" (
    loan_id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES "Assets"("AssetId"), 
    user_id INTEGER NOT NULL REFERENCES "Users"("UserId"),
    lender_name VARCHAR(255),
    loan_name VARCHAR(255),
    loan_type VARCHAR(100),
    loan_amount DECIMAL(18, 2),
    interest_rate DECIMAL(10, 4),
    loan_term_years INTEGER,
    remaining_balance DECIMAL(18, 2),
    monthly_payment DECIMAL(18, 2),
    payment_frequency VARCHAR(50),
    loan_status VARCHAR(50),
    last_payment_date DATE,
    last_payment_amount DECIMAL(18, 2),
    next_payment_date DATE,
    loan_start_date DATE,
    loan_end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

async def init_db():
    if not DATABASE_URL:
        logger.error("POSTGRE_SQL_CONNECTIONSTRING not found in environment variables.")
        return

    logger.info(f"Connecting to database...")
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        logger.info("Cleaning up old/unused tables...")
        # Drop tables we don't use anymore to declutter
        tables_to_drop = [
            "AssetDepreciationSchedule", 
            "LoanProjectedPayments", 
            "ApplicationSettings", 
            "UserPreferences", 
            "ForgotPasswordToken", 
            "vehiclevaluationlog", 
            "equipmentvaluationlog",
            "loaninformation",
            "LoanInformation"
        ]
        
        for table in tables_to_drop:
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE;'))
            await conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE;'))
            
        logger.info("Creating core tables...")
        await conn.execute(text(CREATE_USERS_TABLE_SQL))
        await conn.execute(text(CREATE_ASSETS_TABLE_SQL))
        await conn.execute(text(CREATE_LOANS_TABLE_SQL))
        
        logger.info("Database initialized successfully.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
