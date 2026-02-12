import asyncpg
from typing import List, Optional
from datetime import datetime
from models.asset_models import AssetDTO
import os
from dotenv import load_dotenv

load_dotenv()


class AssetDbContext:
    """Database operations for assets (equivalent to C# AssetDbContext)"""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

    async def get_assets_async(self, user_id: int) -> List[AssetDTO]:
        """Get all non-deleted assets for a user"""
        asset_list = []

        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT
                    "AssetId", "UserId", "Type", "PurchasePrice", "PurchaseDate", "InitialBookValue", "Manufacturer", "Model", "ModelYear",
                    "Usage", "UsageUnit", "Condition", "Country", "StateUs", "ZipCode", "Deleted", "DepreciationMethod", "SalvageValue",
                    "UsefulLife", "DepreciationRate", "TotalExpectedUnitsProduction", "UnitsProducedInYear",
                    "CreatedAt", "UpdatedAt"
                FROM public."Assets"
                WHERE "UserId" = $1 AND "Deleted" <> TRUE
            '''

            rows = await conn.fetch(query, user_id)

            for row in rows:
                asset = AssetDTO(
                    asset_id=row['AssetId'],
                    user_id=row['UserId'],
                    type=row['Type'],
                    purchase_price=float(row['PurchasePrice']),
                    purchase_date=row['PurchaseDate'].strftime("%Y-%m-%d") if row['PurchaseDate'] else None,
                    book_value=float(row['InitialBookValue']),
                    manufacturer=row['Manufacturer'],
                    model=row['Model'],
                    model_year=row['ModelYear'],
                    usage=row['Usage'],
                    usage_unit=row['UsageUnit'],
                    condition=row['Condition'],
                    country=row['Country'],
                    state=row['StateUs'],
                    zip_code=row['ZipCode'],
                    deleted=row['Deleted'],
                    depreciation_method=row['DepreciationMethod'],
                    salvage_value=float(row['SalvageValue']),
                    useful_life=row['UsefulLife'],
                    depreciation_rate=float(row['DepreciationRate']) if row['DepreciationRate'] else None,
                    total_expected_units_of_production=row['TotalExpectedUnitsProduction'] if row['TotalExpectedUnitsProduction'] else 0,
                    units_produced_in_year=row['UnitsProducedInYear'] if row['UnitsProducedInYear'] else 0,
                    create_date=row['CreatedAt'].strftime("%Y-%m-%dT%H:%M:%S"),
                    update_date=row['UpdatedAt'].strftime("%Y-%m-%dT%H:%M:%S")
                )
                asset_list.append(asset)

        finally:
            await conn.close()

        return asset_list

    async def get_asset_async(self, user_id: int, asset: AssetDTO) -> Optional[AssetDTO]:
        """Check if asset already exists (based on unique characteristics)"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT
                    "AssetId", "UserId", "Type", "Manufacturer", "Model", "ModelYear",
                    "Usage", "Condition", "Country", "StateUs", "ZipCode", "CreatedAt"
                FROM public."Assets"
                WHERE "UserId" = $1
                    AND "Type" = $2
                    AND "Manufacturer" = $3
                    AND "Model" = $4
                    AND "ModelYear" = $5
                    AND "Usage" = $6
                    AND "Condition" = $7
                    AND "Country" = $8
                    AND "StateUs" = $9
            '''

            row = await conn.fetchrow(
                query,
                user_id,
                asset.type,
                asset.manufacturer,
                asset.model,
                asset.model_year,
                asset.usage,
                asset.condition,
                asset.country,
                asset.state
            )

            if not row:
                return None

            return AssetDTO(
                asset_id=row['AssetId'],
                user_id=row['UserId'],
                type=row['Type'],
                manufacturer=row['Manufacturer'],
                model=row['Model'],
                model_year=row['ModelYear'],
                usage=row['Usage'],
                condition=row['Condition'],
                country=row['Country'],
                state=row['StateUs'],
                zip_code=row['ZipCode'],
                create_date=row['CreatedAt'].strftime("%Y-%m-%dT%H:%M:%S"),
                book_value=0.0,  # Not needed for existence check
                salvage_value=0.0,
                depreciation_method=""
            )

        finally:
            await conn.close()

    async def get_all_assets_async(self) -> List[AssetDTO]:
        """Get all assets (for background jobs)"""
        asset_list = []

        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT
                    "AssetId", "UserId", "Type", "PurchasePrice", "InitialBookValue", "Manufacturer", "Model", "ModelYear",
                    "Usage", "Condition", "Country", "StateUs", "ZipCode", "Deleted", "DepreciationMethod", "SalvageValue",
                    "UsefulLife", "DepreciationRate", "TotalExpectedUnitsProduction", "UnitsProducedInYear",
                    "CreatedAt", "UpdatedAt"
                FROM public."Assets"
            '''

            rows = await conn.fetch(query)

            for row in rows:
                asset = AssetDTO(
                    asset_id=row['AssetId'],
                    user_id=row['UserId'],
                    type=row['Type'],
                    purchase_price=float(row['PurchasePrice']),
                    book_value=float(row['InitialBookValue']),
                    manufacturer=row['Manufacturer'],
                    model=row['Model'],
                    model_year=row['ModelYear'],
                    usage=row['Usage'],
                    condition=row['Condition'],
                    country=row['Country'],
                    state=row['StateUs'],
                    zip_code=row['ZipCode'],
                    deleted=row['Deleted'],
                    depreciation_method=row['DepreciationMethod'],
                    salvage_value=float(row['SalvageValue']),
                    useful_life=row['UsefulLife'],
                    depreciation_rate=float(row['DepreciationRate']) if row['DepreciationRate'] else None,
                    total_expected_units_of_production=row['TotalExpectedUnitsProduction'] if row['TotalExpectedUnitsProduction'] else 0,
                    units_produced_in_year=row['UnitsProducedInYear'] if row['UnitsProducedInYear'] else 0,
                    create_date=row['CreatedAt'].strftime("%Y-%m-%dT%H:%M:%S"),
                    update_date=row['UpdatedAt'].strftime("%Y-%m-%dT%H:%M:%S")
                )
                asset_list.append(asset)

        finally:
            await conn.close()

        return asset_list

    async def create_asset_async(self, asset: AssetDTO) -> Optional[AssetDTO]:
        """Create a new asset"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                INSERT INTO public."Assets"
                    ("UserId", "Type", "PurchasePrice", "PurchaseDate", "InitialBookValue", "Manufacturer", "Model", "ModelYear", "Usage", "UsageUnit",
                     "Condition", "Country", "StateUs", "ZipCode", "DepreciationMethod", "SalvageValue", "UsefulLife",
                     "DepreciationRate", "TotalExpectedUnitsProduction", "UnitsProducedInYear",
                     "CreatedAt", "UpdatedAt")
                VALUES
                    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
                RETURNING "AssetId"
            '''

            # Parse purchase date or default to now
            try:
                p_date = datetime.strptime(asset.purchase_date, "%Y-%m-%d").date() if asset.purchase_date else datetime.now().date()
            except:
                p_date = datetime.now().date()

            asset_id = await conn.fetchval(
                query,
                asset.user_id,
                asset.type,
                asset.purchase_price,
                p_date,
                asset.book_value,
                asset.manufacturer,
                asset.model,
                asset.model_year,
                asset.usage,
                asset.usage_unit,
                asset.condition,
                asset.country,
                asset.state,
                asset.zip_code,
                asset.depreciation_method,
                asset.salvage_value,
                asset.useful_life,
                asset.depreciation_rate if asset.depreciation_rate else 0,
                asset.total_expected_units_of_production if asset.total_expected_units_of_production else 0,
                asset.units_produced_in_year if asset.units_produced_in_year else 0,
                datetime.now(),
                datetime.now()
            )

            asset.asset_id = asset_id
            return asset

        finally:
            await conn.close()

    async def delete_asset_async(self, asset: AssetDTO) -> None:
        """Soft delete an asset (sets deleted flag to TRUE)"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                UPDATE public."Assets"
                SET "Deleted" = TRUE
                WHERE "UserId" = $1 AND "AssetId" = $2
            '''

            await conn.execute(query, asset.user_id, asset.asset_id)

        finally:
            await conn.close()

    async def update_asset_async(self, asset: AssetDTO) -> AssetDTO:
        """Update an existing asset"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                UPDATE public."Assets"
                SET "Type" = $1,
                    "PurchasePrice" = $2,
                    "PurchaseDate" = $3,
                    "InitialBookValue" = $4,
                    "Manufacturer" = $5,
                    "Model" = $6,
                    "ModelYear" = $7,
                    "Usage" = $8,
                    "UsageUnit" = $9,
                    "Condition" = $10,
                    "Country" = $11,
                    "StateUs" = $12,
                    "ZipCode" = $13,
                    "Deleted" = FALSE,
                    "DepreciationMethod" = $14,
                    "SalvageValue" = $15,
                    "UsefulLife" = $16,
                    "DepreciationRate" = $17,
                    "TotalExpectedUnitsProduction" = $18,
                    "UnitsProducedInYear" = $19,
                    "UpdatedAt" = $20
                WHERE "AssetId" = $21
            '''

            try:
                p_date = datetime.strptime(asset.purchase_date, "%Y-%m-%d").date() if asset.purchase_date else datetime.now().date()
            except:
                p_date = datetime.now().date()

            result = await conn.execute(
                query,
                asset.type,
                asset.purchase_price,
                p_date,
                asset.book_value,
                asset.manufacturer,
                asset.model,
                asset.model_year,
                asset.usage,
                asset.usage_unit,
                asset.condition,
                asset.country,
                asset.state,
                asset.zip_code,
                asset.depreciation_method,
                asset.salvage_value,
                asset.useful_life,
                asset.depreciation_rate if asset.depreciation_rate else 0,
                asset.total_expected_units_of_production if asset.total_expected_units_of_production else 0,
                asset.units_produced_in_year if asset.units_produced_in_year else 0,
                datetime.now(),
                asset.asset_id
            )

            # Check if any rows were updated
            rows_affected = int(result.split()[-1])
            if rows_affected == 0:
                raise Exception(f"No rows were updated for asset {asset.asset_id}")

            return asset

        finally:
            await conn.close()
