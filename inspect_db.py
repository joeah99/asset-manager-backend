import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()

# Get connection string and replace async driver with sync if necessary
DATABASE_URL = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
if DATABASE_URL and "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

def list_tables():
    full_url = DATABASE_URL
    print(f"Connecting to: {full_url.split('@')[-1]}") # Print only host/db part
    engine = create_engine(full_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("TABLES_LIST:", tables)
    if "Assets" in tables:
        cols = [c['name'] for c in inspector.get_columns("Assets")]
        for c in cols:
            print(f"C: {c}")


if __name__ == "__main__":
    list_tables()
