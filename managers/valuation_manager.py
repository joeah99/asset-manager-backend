from typing import List, Optional
from datetime import datetime
from collections import defaultdict
from models.valuation_models import (
    EquipmentValuationDTO,
    MonthlyTotalFMVDTO,
    TotalAssetValueDTO,
    AdjustedForcedLiquidationDTO,
    AdjustedForcedLiquidation
)
from db.valuation_db import ValuationDbContext


class ValuationManager:
    """
    Manager for valuation operations (equivalent to C# ValuationManager)
    Handles valuation queries and aggregations
    """

    def __init__(self, valuation_db_context: ValuationDbContext = None):
        self.valuation_db_context = valuation_db_context or ValuationDbContext()

    async def get_equipment_valuations(self, user_id: int) -> List[EquipmentValuationDTO]:
        """
        Get all equipment valuations for a user

        Args:
            user_id: User ID

        Returns:
            List of equipment valuations
        """
        valuation_list = await self.valuation_db_context.get_equipment_valuations_async(user_id)
        return valuation_list

    async def get_total_fair_market_value(self, user_id: int) -> List[MonthlyTotalFMVDTO]:
        """
        Calculate monthly total fair market value for the last 12 months

        Args:
            user_id: User ID

        Returns:
            List of monthly FMV totals, ordered chronologically (oldest to newest)
        """
        total_fmv_list = await self.get_equipment_valuations(user_id)

        # Group by year and month
        monthly_data = defaultdict(lambda: {"total_fmv": 0.0, "asset_ids": set()})

        for valuation in total_fmv_list:
            if not valuation.valuation_date:
                continue

            year = valuation.valuation_date.year
            month = valuation.valuation_date.month
            key = (year, month)

            monthly_data[key]["total_fmv"] += valuation.adjusted_fair_market_value or 0
            monthly_data[key]["asset_ids"].add(valuation.asset_id)

        # Convert to list of DTOs
        monthly_list = []
        for (year, month), data in monthly_data.items():
            month_name = datetime(year, month, 1).strftime("%B")
            monthly_list.append({
                "year": year,
                "month_number": month,
                "month_name": month_name,
                "total_fmv": data["total_fmv"],
                "num_assets": len(data["asset_ids"])
            })

        # Sort by date descending, take latest 12 months
        monthly_list.sort(key=lambda x: datetime(x["year"], x["month_number"], 1), reverse=True)
        latest_12 = monthly_list[:12]

        # Re-sort chronologically (oldest to newest)
        latest_12.sort(key=lambda x: datetime(x["year"], x["month_number"], 1))

        # Convert to DTOs
        result = [
            MonthlyTotalFMVDTO(
                month=item["month_name"],
                total_fair_market_value=item["total_fmv"],
                number_of_assets=item["num_assets"]
            )
            for item in latest_12
        ]

        return result

    async def get_total_asset_value(self, user_id: int) -> Optional[TotalAssetValueDTO]:
        """
        Calculate total asset value and year-over-year change

        Args:
            user_id: User ID

        Returns:
            Total asset value with percent change from first to last month
        """
        total_fmv_list = await self.get_total_fair_market_value(user_id)

        if not total_fmv_list or len(total_fmv_list) == 0:
            return None

        # Assumes list is chronologically ordered (oldest first, latest last)
        first_value = total_fmv_list[0].total_fair_market_value
        asset_value = total_fmv_list[-1].total_fair_market_value

        # Calculate percent change
        percent_change = 0
        if first_value != 0:
            percent_change = int(round(((asset_value - first_value) / first_value) * 100.0))

        return TotalAssetValueDTO(
            total_asset_value=asset_value,
            percent_change_past_year=percent_change
        )

    async def get_adjusted_forced_liquidation_async(self, user_id: int) -> List[AdjustedForcedLiquidationDTO]:
        """
        Get adjusted forced liquidation values for all user assets

        Args:
            user_id: User ID

        Returns:
            List of adjusted forced liquidation values
        """
        valuation_list = await self.valuation_db_context.get_adjusted_forced_liquidation_async(user_id)

        # Convert to DTOs and sort by asset ID
        response_list = [
            AdjustedForcedLiquidationDTO(
                asset_id=v.asset_id,
                valuation_date=v.valuation_date.strftime("%Y-%m-%d"),
                adjusted_forced_liquidation_value=v.adjusted_forced_liquidation_value
            )
            for v in valuation_list
        ]

        # Sort by asset ID
        response_list.sort(key=lambda x: x.asset_id)

        return response_list
