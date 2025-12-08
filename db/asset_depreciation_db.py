import asyncpg
from typing import List, Optional
from datetime import datetime
from models.asset_models import (
    AssetDepreciationScheduleDTO,
    DepreciationScheduleWithIdDTO
)
import os
from dotenv import load_dotenv

load_dotenv()


class AssetDepreciationScheduleDbContext:
    """
    Database context for asset depreciation schedule operations
    (equivalent to C# AssetDepreciationScheduleDbContext)
    """

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

    async def create_asset_depreciation_schedule_async(
        self,
        schedule: AssetDepreciationScheduleDTO
    ) -> AssetDepreciationScheduleDTO:
        """
        Create a new depreciation schedule entry

        Args:
            schedule: Depreciation schedule entry to create

        Returns:
            Created schedule entry with generated ID
        """
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                INSERT INTO asset_depreciation_schedule
                    (asset_id, depreciation_date, new_book_value, created_at)
                VALUES
                    ($1, $2, $3, NOW())
                RETURNING asset_depreciation_schedule_id
            '''

            schedule_id = await conn.fetchval(
                query,
                schedule.asset_id,
                schedule.depreciation_date,
                schedule.new_book_value
            )

            schedule.asset_depreciation_schedule_id = schedule_id
            return schedule

        finally:
            await conn.close()

    async def get_asset_depreciation_schedule_async(
        self,
        asset_id: int
    ) -> List[AssetDepreciationScheduleDTO]:
        """
        Get depreciation schedule for an asset

        Args:
            asset_id: Asset ID

        Returns:
            List of depreciation schedule entries
        """
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT
                    asset_depreciation_schedule_id,
                    asset_id,
                    depreciation_date,
                    new_book_value,
                    created_at
                FROM asset_depreciation_schedule
                WHERE asset_id = $1
                ORDER BY depreciation_date
            '''

            rows = await conn.fetch(query, asset_id)

            schedule_list = []
            for row in rows:
                schedule_list.append(AssetDepreciationScheduleDTO(
                    asset_depreciation_schedule_id=row['asset_depreciation_schedule_id'],
                    asset_id=row['asset_id'],
                    depreciation_date=row['depreciation_date'],
                    new_book_value=row['new_book_value'] if row['new_book_value'] is not None else 0.0,
                    created_at=row['created_at']
                ))

            return schedule_list

        finally:
            await conn.close()

    async def delete_asset_depreciation_schedule_async(self, asset_id: int) -> bool:
        """
        Delete all depreciation schedules for an asset

        Args:
            asset_id: Asset ID

        Returns:
            True if any rows were deleted
        """
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                DELETE FROM asset_depreciation_schedule
                WHERE asset_id = $1
            '''

            result = await conn.execute(query, asset_id)
            # Result format is "DELETE N" where N is number of rows
            rows_affected = int(result.split()[-1]) if result else 0
            return rows_affected > 0

        finally:
            await conn.close()

    async def get_asset_depreciation_async(
        self,
        user_id: int
    ) -> List[DepreciationScheduleWithIdDTO]:
        """
        Get all depreciation schedules for all of a user's assets

        Args:
            user_id: User ID

        Returns:
            List of depreciation schedule entries with asset IDs
        """
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT
                    ads.asset_id,
                    ads.depreciation_date,
                    ads.new_book_value
                FROM asset_depreciation_schedule AS ads
                WHERE ads.asset_id IN (
                    SELECT asset_id FROM public."Asset" WHERE user_id = $1
                )
                ORDER BY ads.asset_id, ads.depreciation_date
            '''

            rows = await conn.fetch(query, user_id)

            depreciation_list = []
            for row in rows:
                depreciation_list.append(DepreciationScheduleWithIdDTO(
                    asset_id=row['asset_id'],
                    depreciation_date=row['depreciation_date'],
                    new_book_value=row['new_book_value'] if row['new_book_value'] is not None else 0.0
                ))

            return depreciation_list

        finally:
            await conn.close()
