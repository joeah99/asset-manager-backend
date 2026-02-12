import asyncio
import asyncpg
import logging

# Hardcoded from .env to bypass dotenv issues
DATABASE_URL = "postgresql://postgres.atxptziodoyjdiwrmbfw:r2N%2A%26P6qruV%2AA%23a@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_db():
    logger.info(f"Connecting to database...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Connected successfully.")
        
        # Drop table if exists
        logger.info("Dropping table if exists...")
        await conn.execute('DROP TABLE IF EXISTS LoanInformation CASCADE;')
        
        # Create table
        logger.info("Creating table...")
        CREATE_LOAN_INFORMATION_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS LoanInformation (
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
        await conn.execute(CREATE_LOAN_INFORMATION_TABLE_SQL)
        logger.info("Table LoanInformation created successfully.")
        
        await conn.close()
    except Exception as e:
        logger.error(f"Error updating DB: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(update_db())
