import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
if DATABASE_URL and "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

def drop_duplicates():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Dropping table 'Asset' if exists...")
        conn.execute(text('DROP TABLE IF EXISTS "Asset" CASCADE'))
        print("Dropping table 'User' if exists...")
        conn.execute(text('DROP TABLE IF EXISTS "User" CASCADE'))
        conn.commit()
    print("Done.")

if __name__ == "__main__":
    drop_duplicates()
