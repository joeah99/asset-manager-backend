import asyncio
import asyncpg
import logging

# Hardcoded from .env to bypass dotenv issues - reusing same string
DATABASE_URL = "postgresql://postgres.atxptziodoyjdiwrmbfw:r2N%2A%26P6qruV%2AA%23a@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_loans_table():
    logger.info(f"Connecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Connected successfully.")
        
        # 1. Rename table if old one exists and new one doesn't
        # Checking if 'LoanInformation' exists
        check_old = await conn.fetchval("SELECT to_regclass('public.LoanInformation')")
        check_new = await conn.fetchval("SELECT to_regclass('public.Loans')")
        
        if check_old and not check_new:
             logger.info("Renaming LoanInformation to Loans...")
             await conn.execute('ALTER TABLE "LoanInformation" RENAME TO "Loans";')
        elif not check_old and not check_new:
             logger.info("Creating Loans table (neither existed)...")
             # Create from scratch
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
        else:
             logger.info("Loans table likely already exists or state is mixed.")
        
        # Verify
        final_check = await conn.fetchval("SELECT to_regclass('public.Loans')")
        if final_check:
             logger.info("SUCCESS: 'Loans' table exists.")
        else:
             logger.error("FAILURE: 'Loans' table does not exist.")

        # Cleanup old references just in case (though rename handles it)
        # await conn.execute('DROP TABLE IF EXISTS "LoanInformation" CASCADE;') 
        
        await conn.close()
    except Exception as e:
        logger.error(f"Error migrating DB: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_loans_table())
