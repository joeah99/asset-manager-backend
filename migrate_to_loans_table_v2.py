import asyncio
import asyncpg
import logging

# Hardcoded from .env to bypass dotenv issues - reusing same string
DATABASE_URL = "postgresql://postgres.atxptziodoyjdiwrmbfw:r2N%2A%26P6qruV%2AA%23a@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_loans_table():
    logger.info(f"Connecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Connected successfully.")
        
        # Check current tables
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        table_names = [t['table_name'] for t in tables]
        logger.info(f"Existing tables: {table_names}")

        if "loaninformation" in table_names:
             logger.info("Found 'loaninformation' (lowercase). Renaming to 'Loans'...")
             await conn.execute('ALTER TABLE "loaninformation" RENAME TO "Loans";')
        elif "LoanInformation" in table_names:
            logger.info("Found 'LoanInformation' (proper case). Renaming to 'Loans'...")
            await conn.execute('ALTER TABLE "LoanInformation" RENAME TO "Loans";')
        elif "Loans" in table_names:
            logger.info("'Loans' table already exists.")
        else:
            logger.warning("Could not find 'LoanInformation' or 'Loans'. Maybe it was deleted?")
            # Create if missing
            logger.info("Creating 'Loans' table from scratch...")
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
            await conn.execute(CREATE_LOANS_TABLE_SQL)

        await conn.close()
    except Exception as e:
        logger.error(f"Error migrating DB: {e}")
        # raise # Don't raise, just log so we can see output

if __name__ == "__main__":
    asyncio.run(migrate_loans_table())
