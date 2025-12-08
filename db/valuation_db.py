import asyncpg
from typing import List
from datetime import datetime
from models.valuation_models import (
    EquipmentValuationDTO,
    VehicleValuationDTO,
    AdjustedForcedLiquidation
)
import os
from dotenv import load_dotenv

load_dotenv()


class ValuationDbContext:
    """Database operations for valuations (equivalent to C# ValuationDbContext)"""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

    async def get_equipment_valuations_async(self, user_id: int) -> List[EquipmentValuationDTO]:
        """Get all equipment valuations for a user's assets"""
        valuations_list = []

        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT
                    log_id, asset_id, valuation_date, unadjusted_fair_market_value,
                    unadjusted_orderly_liquidation_value, unadjusted_forced_liquidation_value,
                    adjusted_fair_market_value, adjusted_orderly_liquidation_value,
                    adjusted_forced_liquidation_value, salvage
                FROM "EquipmentValuationLog"
                WHERE asset_id IN (
                    SELECT asset_id FROM "Asset" WHERE user_id = $1
                )
            '''

            rows = await conn.fetch(query, user_id)

            for row in rows:
                valuation = EquipmentValuationDTO(
                    log_id=row['log_id'],
                    asset_id=row['asset_id'],
                    valuation_date=row['valuation_date'],
                    unadjusted_fair_market_value=float(row['unadjusted_fair_market_value']) if row['unadjusted_fair_market_value'] else 0,
                    unadjusted_orderly_liquidation_value=float(row['unadjusted_orderly_liquidation_value']) if row['unadjusted_orderly_liquidation_value'] else 0,
                    unadjusted_forced_liquidation_value=float(row['unadjusted_forced_liquidation_value']) if row['unadjusted_forced_liquidation_value'] else 0,
                    adjusted_fair_market_value=float(row['adjusted_fair_market_value']) if row['adjusted_fair_market_value'] else 0,
                    adjusted_orderly_liquidation_value=float(row['adjusted_orderly_liquidation_value']) if row['adjusted_orderly_liquidation_value'] else 0,
                    adjusted_forced_liquidation_value=float(row['adjusted_forced_liquidation_value']) if row['adjusted_forced_liquidation_value'] else 0,
                    salvage=float(row['salvage']) if row['salvage'] else 0
                )
                valuations_list.append(valuation)

        finally:
            await conn.close()

        return valuations_list

    async def insert_equipment_valuation_async(self, valuation: EquipmentValuationDTO, asset_id: int) -> None:
        """Insert equipment valuation into database"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                INSERT INTO "EquipmentValuationLog"
                    (asset_id, unadjusted_fair_market_value, unadjusted_orderly_liquidation_value,
                     unadjusted_forced_liquidation_value, adjusted_fair_market_value,
                     adjusted_orderly_liquidation_value, adjusted_forced_liquidation_value,
                     salvage, valuation_date)
                VALUES
                    ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            '''

            await conn.execute(
                query,
                asset_id,
                valuation.unadjusted_fair_market_value or 0,
                valuation.unadjusted_orderly_liquidation_value or 0,
                valuation.unadjusted_forced_liquidation_value or 0,
                valuation.adjusted_fair_market_value or 0,
                valuation.adjusted_orderly_liquidation_value or 0,
                valuation.adjusted_forced_liquidation_value or 0,
                valuation.salvage or 0,
                datetime.utcnow()
            )

        finally:
            await conn.close()

    async def insert_vehicle_valuation_async(self, valuation: VehicleValuationDTO, asset_id: int) -> None:
        """Insert vehicle valuation into database"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                INSERT INTO "VehicleValuationLog"
                    (asset_id, unadjusted_low, unadjusted_high, unadjusted_finance,
                     unadjusted_retail, unadjusted_wholesale, unadjusted_trade_in,
                     adjusted_low, adjusted_high, adjusted_finance, adjusted_retail,
                     adjusted_wholesale, adjusted_trade_in, valuation_date)
                VALUES
                    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            '''

            await conn.execute(
                query,
                asset_id,
                valuation.unadjusted_low or 0,
                valuation.unadjusted_high or 0,
                valuation.unadjusted_finance or 0,
                valuation.unadjusted_retail or 0,
                valuation.unadjusted_wholesale or 0,
                valuation.unadjusted_trade_in or 0,
                valuation.adjusted_low or 0,
                valuation.adjusted_high or 0,
                valuation.adjusted_finance or 0,
                valuation.adjusted_retail or 0,
                valuation.adjusted_wholesale or 0,
                valuation.adjusted_trade_in or 0,
                datetime.utcnow()
            )

        finally:
            await conn.close()

    async def get_adjusted_forced_liquidation_async(self, user_id: int) -> List[AdjustedForcedLiquidation]:
        """Get adjusted forced liquidation values for all user's assets"""
        adjusted_list = []

        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT
                    asset_id, valuation_date, adjusted_forced_liquidation_value
                FROM "EquipmentValuationLog"
                WHERE asset_id IN (
                    SELECT asset_id FROM "Asset" WHERE user_id = $1
                )
            '''

            rows = await conn.fetch(query, user_id)

            for row in rows:
                dto = AdjustedForcedLiquidation(
                    asset_id=row['asset_id'],
                    valuation_date=row['valuation_date'],
                    adjusted_forced_liquidation_value=float(row['adjusted_forced_liquidation_value']) if row['adjusted_forced_liquidation_value'] else 0
                )
                adjusted_list.append(dto)

        finally:
            await conn.close()

        return adjusted_list
