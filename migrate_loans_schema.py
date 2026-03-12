"""
Migration script to add linked_type and linked_id to Loans table
Run this script to update the schema for linking loans to both assets and purchases
"""
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    db_url = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
    if not db_url:
        print("Error: POSTGRE_SQL_CONNECTIONSTRING not found")
        return
    
    conn = await asyncpg.connect(db_url)
    
    try:
        print("Running migration: add linked_type and linked_id to Loans...")
        
        # Step 1: Add new columns
        await conn.execute("""
            ALTER TABLE "Loans" 
            ADD COLUMN IF NOT EXISTS linked_type VARCHAR(20),
            ADD COLUMN IF NOT EXISTS linked_id INTEGER;
        """)
        print("✓ Added linked_type and linked_id columns")
        
        # Step 2: Migrate existing data
        result = await conn.execute("""
            UPDATE "Loans"
            SET linked_type = 'asset',
                linked_id = asset_id
            WHERE asset_id IS NOT NULL AND linked_type IS NULL;
        """)
        print(f"✓ Migrated existing asset_id data: {result}")
        
        # Step 3: Drop the old asset_id column
        await conn.execute("""
            ALTER TABLE "Loans" DROP COLUMN IF EXISTS asset_id;
        """)
        print("✓ Dropped old asset_id column")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
