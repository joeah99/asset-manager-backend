import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

async def run_migration():
    print(f"Connecting to database...")
    conn = await asyncpg.connect(CONNECTION_STRING)
    try:
        print("Checking if zip_code column exists...")
        # Check if column exists
        check_query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='Asset' AND column_name='zip_code';
        """
        row = await conn.fetchrow(check_query)
        
        if row:
            print("Column 'zip_code' already exists. Skipping migration.")
        else:
            print("Adding 'zip_code' column to 'Asset' table...")
            alter_query = 'ALTER TABLE public."Asset" ADD COLUMN zip_code VARCHAR(10);'
            await conn.execute(alter_query)
            print("Migration successful! 'zip_code' column added.")

    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
