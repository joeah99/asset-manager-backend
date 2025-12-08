from typing import List
from datetime import datetime
from models.asset_models import (
    AssetDTO,
    AssetDepreciationDTO,
    AssetDepreciationScheduleDTO
)
from db.asset_depreciation_db import AssetDepreciationScheduleDbContext
from services.asset_depreciation_service import AssetDepreciationService


class AssetDepreciationManager:
    """
    Manager for asset depreciation operations
    (equivalent to C# AssetDepreciationManager)

    Handles depreciation schedule creation, retrieval, and updates
    """

    def __init__(
        self,
        schedule_db_context: AssetDepreciationScheduleDbContext = None,
        depreciation_service: AssetDepreciationService = None
    ):
        self.schedule_db_context = schedule_db_context or AssetDepreciationScheduleDbContext()
        self.depreciation_service = depreciation_service or AssetDepreciationService()

    async def create_asset_depreciation_schedule(self, asset: AssetDTO) -> AssetDTO:
        """
        Create depreciation schedule for an asset based on its depreciation method

        Args:
            asset: Asset with depreciation parameters

        Returns:
            Asset with populated depreciation schedule

        Raises:
            ValueError: If depreciation method is invalid or required parameters are missing
            Exception: If schedule creation fails
        """
        end_of_month_values: List[AssetDepreciationDTO] = []

        # Calculate depreciation based on method
        if asset.depreciation_method == "StraightLine":
            # Clear unused fields
            asset.depreciation_rate = 0
            asset.units_produced_in_year = 0
            asset.total_expected_units_of_production = 0

            if asset.useful_life is None:
                raise ValueError("Useful life is required for straight-line depreciation.")

            end_of_month_values = self.depreciation_service.straight_line_depreciation(
                float(asset.book_value),
                float(asset.salvage_value),
                asset.useful_life
            )

        elif asset.depreciation_method == "DecliningBalance":
            # Clear unused fields
            asset.total_expected_units_of_production = 0
            asset.units_produced_in_year = 0

            if asset.useful_life is None or asset.depreciation_rate is None:
                raise ValueError("Useful life and depreciation rate are required for declining balance depreciation.")

            end_of_month_values = self.depreciation_service.declining_balance_depreciation(
                float(asset.book_value),
                float(asset.salvage_value),
                asset.useful_life,
                asset.depreciation_rate
            )

        elif asset.depreciation_method == "DoubleDecliningBalance":
            # Clear unused fields
            asset.depreciation_rate = 0
            asset.units_produced_in_year = 0
            asset.total_expected_units_of_production = 0

            if asset.useful_life is None:
                raise ValueError("Useful life is required for double declining balance depreciation.")

            end_of_month_values = self.depreciation_service.double_declining_balance_depreciation(
                float(asset.book_value),
                float(asset.salvage_value),
                asset.useful_life
            )

        elif asset.depreciation_method == "UnitsOfProduction":
            # Clear unused fields
            asset.depreciation_rate = 0
            asset.useful_life = 0

            if asset.total_expected_units_of_production is None or asset.units_produced_in_year is None:
                raise ValueError("Total expected units of production and units produced in year are required for units of production depreciation.")

            end_of_month_values = self.depreciation_service.units_of_production_depreciation(
                float(asset.book_value),
                float(asset.salvage_value),
                asset.total_expected_units_of_production,
                asset.units_produced_in_year
            )

        else:
            raise ValueError(f"Invalid depreciation method: {asset.depreciation_method}")

        # Save to database if we have a valid asset ID
        if len(end_of_month_values) > 0:
            if asset.asset_id > 0:
                for depreciation_dto in end_of_month_values:
                    schedule_entry = AssetDepreciationScheduleDTO(
                        asset_depreciation_schedule_id=0,
                        asset_id=asset.asset_id,
                        depreciation_date=depreciation_dto.depreciation_date,
                        new_book_value=depreciation_dto.new_book_value,
                        created_at=datetime.now()
                    )
                    await self.schedule_db_context.create_asset_depreciation_schedule_async(schedule_entry)

                # Populate the asset's depreciation schedule
                asset.asset_depreciation_schedule = end_of_month_values
                return asset
            else:
                raise Exception("Failed to create asset depreciation - invalid asset ID.")
        else:
            raise Exception("Failed to calculate depreciation schedule.")

    async def get_asset_depreciation_schedule(self, asset_id: int) -> List[AssetDepreciationScheduleDTO]:
        """
        Get depreciation schedule for an asset

        Args:
            asset_id: Asset ID

        Returns:
            List of depreciation schedule entries

        Raises:
            Exception: If schedule not found
        """
        schedule = await self.schedule_db_context.get_asset_depreciation_schedule_async(asset_id)

        if schedule is not None:
            return schedule
        else:
            raise Exception("Asset depreciation schedule not found.")

    async def update_asset_depreciation_record(self, asset: AssetDTO) -> AssetDTO:
        """
        Update depreciation schedule for an asset

        Deletes existing schedule and creates new one based on updated parameters

        Args:
            asset: Asset with updated depreciation parameters

        Returns:
            Asset with updated depreciation schedule

        Raises:
            ValueError: If depreciation method is invalid or required parameters are missing
            Exception: If update fails
        """
        if asset.asset_id <= 0:
            raise Exception("Asset depreciation record not found - invalid asset ID.")

        end_of_month_values: List[AssetDepreciationDTO] = []

        # Calculate depreciation based on method
        if asset.depreciation_method == "StraightLine":
            # Clear unused fields
            asset.depreciation_rate = 0
            asset.units_produced_in_year = 0
            asset.total_expected_units_of_production = 0

            if asset.useful_life is None:
                raise ValueError("Useful life is required for straight-line depreciation.")

            end_of_month_values = self.depreciation_service.straight_line_depreciation(
                float(asset.book_value),
                float(asset.salvage_value),
                asset.useful_life
            )

        elif asset.depreciation_method == "DecliningBalance":
            # Clear unused fields
            asset.total_expected_units_of_production = 0
            asset.units_produced_in_year = 0

            if asset.useful_life is None or asset.depreciation_rate is None:
                raise ValueError("Useful life and depreciation rate are required for declining balance depreciation.")

            end_of_month_values = self.depreciation_service.declining_balance_depreciation(
                float(asset.book_value),
                float(asset.salvage_value),
                asset.useful_life,
                asset.depreciation_rate
            )

        elif asset.depreciation_method == "DoubleDecliningBalance":
            # Clear unused fields
            asset.depreciation_rate = 0
            asset.units_produced_in_year = 0
            asset.total_expected_units_of_production = 0

            if asset.useful_life is None:
                raise ValueError("Useful life is required for double declining balance depreciation.")

            end_of_month_values = self.depreciation_service.double_declining_balance_depreciation(
                float(asset.book_value),
                float(asset.salvage_value),
                asset.useful_life
            )

        elif asset.depreciation_method == "UnitsOfProduction":
            # Clear unused fields
            asset.depreciation_rate = 0
            asset.useful_life = 0

            if asset.total_expected_units_of_production is None or asset.units_produced_in_year is None:
                raise ValueError("Total expected units of production and units produced in year are required for units of production depreciation.")

            end_of_month_values = self.depreciation_service.units_of_production_depreciation(
                float(asset.book_value),
                float(asset.salvage_value),
                asset.total_expected_units_of_production,
                asset.units_produced_in_year
            )

        else:
            raise ValueError(f"Invalid depreciation method: {asset.depreciation_method}")

        # Update database
        if len(end_of_month_values) > 0:
            # Delete old schedule
            await self.schedule_db_context.delete_asset_depreciation_schedule_async(asset.asset_id)

            # Create new schedule entries
            for depreciation_dto in end_of_month_values:
                schedule_entry = AssetDepreciationScheduleDTO(
                    asset_depreciation_schedule_id=0,
                    asset_id=asset.asset_id,
                    depreciation_date=depreciation_dto.depreciation_date,
                    new_book_value=depreciation_dto.new_book_value,
                    created_at=datetime.now()
                )
                await self.schedule_db_context.create_asset_depreciation_schedule_async(schedule_entry)

            # Populate the asset's depreciation schedule
            asset.asset_depreciation_schedule = end_of_month_values
            return asset
        else:
            raise Exception("Failed to calculate depreciation schedule.")
