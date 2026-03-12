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
    "CreatedDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    loan_start_date DATE,
    loan_end_date DATE,
    ltv DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_PURCHASES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS "Purchases" (
    "purchase_id" SERIAL PRIMARY KEY,
    "user_id" INTEGER NOT NULL REFERENCES "Users"("UserId"),
    "asset_name" VARCHAR(255),
    "asset_type" VARCHAR(100),
    "manufacturer" VARCHAR(100),
    "model" VARCHAR(100),
    "model_year" VARCHAR(10),
    "usage" DECIMAL(18, 2),
    "usage_unit" VARCHAR(50),
    "cost" DECIMAL(18, 2),
    "depreciation_method" VARCHAR(50),
    "business_use_percent" DECIMAL(5, 2),
    "in_service_month" VARCHAR(7),
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "PurchaseType" VARCHAR(50) DEFAULT 'REPLACEMENT'
);
"""

CREATE_TAX_POLICY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS "TaxPolicyYear" (
    "tax_year"                        INTEGER PRIMARY KEY,
    "section_179_limit"               INTEGER NOT NULL,
    "section_179_phaseout_threshold"  INTEGER NOT NULL,
    "bonus_depreciation_percent"      INTEGER NOT NULL,
    "macrs_5yr_schedule"              JSONB NOT NULL,
    "macrs_7yr_schedule"              JSONB NOT NULL,
    "federal_brackets"                JSONB NOT NULL,
    "policy_source"                   VARCHAR(255) DEFAULT 'IRS Publication 946',
    "last_updated"                    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

async def init_db():
    db_url = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
    
    if not db_url:
        logger.error("POSTGRE_SQL_CONNECTIONSTRING not found in environment variables.")
        return

    # Adjust connection string for SQLAlchemy async engine
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    logger.info(f"Connecting to database...")
    engine = create_async_engine(db_url, echo=False)

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
        
        # Drop obsolete Asset columns from existing database
        for col in ["StateUs", "Deleted", "SalvageValue", "DepreciationRate", "TotalExpectedUnitsProduction", "UnitsProducedInYear", "IsDeleted"]:
            await conn.execute(text(f'ALTER TABLE "Assets" DROP COLUMN IF EXISTS "{col}";'))
            
        await conn.execute(text(CREATE_LOANS_TABLE_SQL))
        await conn.execute(text('ALTER TABLE "Loans" ADD COLUMN IF NOT EXISTS ltv DECIMAL(10, 4);'))
        
        # Drop obsolete Loan columns from existing database
        for col in ["last_payment_date", "last_payment_amount", "next_payment_date", "purchase_id"]:
            await conn.execute(text(f'ALTER TABLE "Loans" DROP COLUMN IF EXISTS "{col}";'))
            
        await conn.execute(text(CREATE_PURCHASES_TABLE_SQL))
        await conn.execute(text(CREATE_TAX_POLICY_TABLE_SQL))
        
        logger.info("Database initialized successfully.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
