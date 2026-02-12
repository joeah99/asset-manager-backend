import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
if DATABASE_URL and "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

def recreate_assets_table():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Dropping existing 'Assets' table...")
        conn.execute(text('DROP TABLE IF EXISTS "Assets" CASCADE'))
        
        print("Creating 'Assets' table with correct schema...")
        # Schema matches AssetDTO and AssetDbContext queries (PascalCase)
        create_query = """
        CREATE TABLE "Assets" (
            "AssetId" SERIAL PRIMARY KEY,
            "UserId" INTEGER NOT NULL,
            "Type" VARCHAR(50) NOT NULL,
            "PurchasePrice" DECIMAL(18, 2) NOT NULL,
            "PurchaseDate" DATE NOT NULL DEFAULT CURRENT_DATE,
            "InitialBookValue" DECIMAL(18, 2) NOT NULL,
            "Manufacturer" VARCHAR(100) NOT NULL,
            "Model" VARCHAR(100) NOT NULL,
            "ModelYear" VARCHAR(4) NOT NULL,
            "Usage" INTEGER NOT NULL DEFAULT 0,
            "UsageUnit" VARCHAR(20) NOT NULL DEFAULT 'hours',
            "Condition" VARCHAR(50) NOT NULL,
            "Country" VARCHAR(50) NOT NULL,
            "StateUs" VARCHAR(50) NOT NULL,
            "ZipCode" VARCHAR(20) NOT NULL,
            "Deleted" BOOLEAN NOT NULL DEFAULT FALSE,
            "DepreciationMethod" VARCHAR(50) NOT NULL,
            "SalvageValue" DECIMAL(18, 2) NOT NULL DEFAULT 0,
            "UsefulLife" INTEGER NOT NULL,
            "DepreciationRate" DECIMAL(5, 2),
            "TotalExpectedUnitsProduction" INTEGER,
            "UnitsProducedInYear" INTEGER,
            "CreatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
            "UpdatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
            
            CONSTRAINT fk_user
                FOREIGN KEY("UserId") 
                REFERENCES "Users"("UserId")
                ON DELETE CASCADE
        );
        """
        conn.execute(text(create_query))
        conn.commit()
        print("Assets table created successfully.")

if __name__ == "__main__":
    recreate_assets_table()
