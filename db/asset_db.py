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
                    asset_id, user_id, asset_type, initial_book_value, manufacturer, model, model_year,
                    usage, condition, country, state_us, deleted, depreciation_method, salvage_value,
                    useful_life, depreciation_rate, total_expected_units_production, units_produced_in_year,
                    created_at, updated_at
                FROM public."Asset"
                WHERE user_id = $1 AND deleted <> TRUE
            '''

            rows = await conn.fetch(query, user_id)

            for row in rows:
                asset = AssetDTO(
                    asset_id=row['asset_id'],
                    user_id=row['user_id'],
                    type=row['asset_type'],
                    book_value=float(row['initial_book_value']),
                    manufacturer=row['manufacturer'],
                    model=row['model'],
                    model_year=row['model_year'],
                    usage=row['usage'],
                    condition=row['condition'],
                    country=row['country'],
                    state=row['state_us'],
                    deleted=row['deleted'],
                    depreciation_method=row['depreciation_method'],
                    salvage_value=float(row['salvage_value']),
                    useful_life=row['useful_life'],
                    depreciation_rate=float(row['depreciation_rate']) if row['depreciation_rate'] else None,
                    total_expected_units_of_production=row['total_expected_units_production'] if row['total_expected_units_production'] else 0,
                    units_produced_in_year=row['units_produced_in_year'] if row['units_produced_in_year'] else 0,
                    create_date=row['created_at'].strftime("%Y-%m-%dT%H:%M:%S"),
                    update_date=row['updated_at'].strftime("%Y-%m-%dT%H:%M:%S")
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
                    asset_id, user_id, asset_type, manufacturer, model, model_year,
                    usage, condition, country, state_us, created_at
                FROM public."Asset"
                WHERE user_id = $1
                    AND asset_type = $2
                    AND manufacturer = $3
                    AND model = $4
                    AND model_year = $5
                    AND usage = $6
                    AND condition = $7
                    AND country = $8
                    AND state_us = $9
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
                asset_id=row['asset_id'],
                user_id=row['user_id'],
                type=row['asset_type'],
                manufacturer=row['manufacturer'],
                model=row['model'],
                model_year=row['model_year'],
                usage=row['usage'],
                condition=row['condition'],
                country=row['country'],
                state=row['state_us'],
                create_date=row['created_at'].strftime("%Y-%m-%dT%H:%M:%S"),
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
                    asset_id, user_id, asset_type, initial_book_value, manufacturer, model, model_year,
                    usage, condition, country, state_us, deleted, depreciation_method, salvage_value,
                    useful_life, depreciation_rate, total_expected_units_production, units_produced_in_year,
                    created_at, updated_at
                FROM public."Asset"
            '''

            rows = await conn.fetch(query)

            for row in rows:
                asset = AssetDTO(
                    asset_id=row['asset_id'],
                    user_id=row['user_id'],
                    type=row['asset_type'],
                    book_value=float(row['initial_book_value']),
                    manufacturer=row['manufacturer'],
                    model=row['model'],
                    model_year=row['model_year'],
                    usage=row['usage'],
                    condition=row['condition'],
                    country=row['country'],
                    state=row['state_us'],
                    deleted=row['deleted'],
                    depreciation_method=row['depreciation_method'],
                    salvage_value=float(row['salvage_value']),
                    useful_life=row['useful_life'],
                    depreciation_rate=float(row['depreciation_rate']) if row['depreciation_rate'] else None,
                    total_expected_units_of_production=row['total_expected_units_production'] if row['total_expected_units_production'] else 0,
                    units_produced_in_year=row['units_produced_in_year'] if row['units_produced_in_year'] else 0,
                    create_date=row['created_at'].strftime("%Y-%m-%dT%H:%M:%S"),
                    update_date=row['updated_at'].strftime("%Y-%m-%dT%H:%M:%S")
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
                INSERT INTO public."Asset"
                    (user_id, asset_type, initial_book_value, manufacturer, model, model_year, usage,
                     condition, country, state_us, depreciation_method, salvage_value, useful_life,
                     depreciation_rate, total_expected_units_production, units_produced_in_year,
                     created_at, updated_at)
                VALUES
                    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                RETURNING asset_id
            '''

            asset_id = await conn.fetchval(
                query,
                asset.user_id,
                asset.type,
                asset.book_value,
                asset.manufacturer,
                asset.model,
                asset.model_year,
                asset.usage,
                asset.condition,
                asset.country,
                asset.state,
                asset.depreciation_method,
                asset.salvage_value,
                asset.useful_life,
                asset.depreciation_rate,
                asset.total_expected_units_of_production,
                asset.units_produced_in_year,
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
                UPDATE public."Asset"
                SET deleted = TRUE
                WHERE user_id = $1 AND asset_id = $2
            '''

            await conn.execute(query, asset.user_id, asset.asset_id)

        finally:
            await conn.close()

    async def update_asset_async(self, asset: AssetDTO) -> AssetDTO:
        """Update an existing asset"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                UPDATE public."Asset"
                SET asset_type = $1,
                    initial_book_value = $2,
                    manufacturer = $3,
                    model = $4,
                    model_year = $5,
                    usage = $6,
                    condition = $7,
                    country = $8,
                    state_us = $9,
                    deleted = FALSE,
                    depreciation_method = $10,
                    salvage_value = $11,
                    useful_life = $12,
                    depreciation_rate = $13,
                    total_expected_units_production = $14,
                    units_produced_in_year = $15,
                    updated_at = $16
                WHERE asset_id = $17
            '''

            result = await conn.execute(
                query,
                asset.type,
                asset.book_value,
                asset.manufacturer,
                asset.model,
                asset.model_year,
                asset.usage,
                asset.condition,
                asset.country,
                asset.state,
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
