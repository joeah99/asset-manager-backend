from typing import List, Optional
from datetime import datetime
from models.asset_models import AssetDTO, FairMarketValueDTO
from db.asset_db import AssetDbContext
from db.valuation_db import ValuationDbContext
from services.asset_valuation_service import AssetValuationService
from managers.asset_depreciation_manager import AssetDepreciationManager


class AssetManager:
    """
    Manager for asset operations (equivalent to C# AssetManager)
    Integrates asset CRUD with valuations and depreciation
    """

    def __init__(
        self,
        asset_db_context: AssetDbContext = None,
        valuation_db_context: ValuationDbContext = None,
        asset_valuation_service: AssetValuationService = None,
        asset_depreciation_manager: AssetDepreciationManager = None
    ):
        self.asset_db_context = asset_db_context or AssetDbContext()
        self.valuation_db_context = valuation_db_context or ValuationDbContext()
        self.asset_valuation_service = asset_valuation_service or AssetValuationService()
        self.asset_depreciation_manager = asset_depreciation_manager or AssetDepreciationManager()

    async def get_assets(self, user_id: int) -> List[AssetDTO]:
        """
        Get all assets for a user

        Args:
            user_id: User ID

        Returns:
            List of assets with valuations and depreciation schedules
        """
        # Get assets from database
        asset_list = await self.asset_db_context.get_assets_async(user_id)

        # TODO: When ValuationController is converted, add:
        # 1. Get valuations for each asset
        # 2. Append fair_market_values_over_time to each asset

        # Get depreciation schedules for each asset
        for asset in asset_list:
            try:
                depreciation_schedule = await self.asset_depreciation_manager.get_asset_depreciation_schedule(asset.asset_id)
                # Convert to AssetDepreciationDTO format
                from models.asset_models import AssetDepreciationDTO
                asset.asset_depreciation_schedule = [
                    AssetDepreciationDTO(
                        depreciation_date=schedule.depreciation_date,
                        new_book_value=schedule.new_book_value
                    )
                    for schedule in depreciation_schedule
                ]
            except Exception:
                # If no depreciation schedule exists, leave empty
                pass

        return asset_list

    async def create_asset(self, asset: AssetDTO) -> Optional[AssetDTO]:
        """
        Create a new asset with automatic valuation

        Args:
            asset: Asset data

        Returns:
            Created asset with valuation and depreciation schedule
        """
        # Check if asset already exists
        existing_asset = await self.asset_db_context.get_asset_async(asset.user_id, asset)

        if existing_asset:
            return None  # Asset already exists

        # Create the asset
        new_asset = await self.asset_db_context.create_asset_async(asset)

        # Get valuation from external API
        try:
            if asset.type == "Equipment":
                equipment_valuation = await self.asset_valuation_service.get_equipment_valuation_async(
                    asset.manufacturer,
                    asset.model,
                    asset.model_year,
                    str(asset.usage),
                    asset.condition,
                    asset.country,
                    asset.state
                )

                await self.valuation_db_context.insert_equipment_valuation_async(
                    equipment_valuation,
                    new_asset.asset_id
                )

                new_asset.fair_market_values_over_time = [
                    FairMarketValueDTO(
                        time_set=datetime.now(),
                        value=equipment_valuation.adjusted_forced_liquidation_value or 0.0
                    )
                ]

            elif asset.type == "Vehicle":
                vehicle_valuation = await self.asset_valuation_service.get_vehicle_valuation_async(
                    asset.manufacturer,
                    asset.model,
                    asset.model_year,
                    str(asset.usage),
                    asset.condition,
                    asset.country,
                    asset.state
                )

                await self.valuation_db_context.insert_vehicle_valuation_async(
                    vehicle_valuation,
                    new_asset.asset_id
                )

                new_asset.fair_market_values_over_time = [
                    FairMarketValueDTO(
                        time_set=datetime.now(),
                        value=vehicle_valuation.adjusted_trade_in or 0.0
                    )
                ]
        except Exception as e:
            # Log error but don't fail asset creation if valuation fails
            print(f"Warning: Failed to fetch valuation for asset {new_asset.asset_id}: {e}")

        # Create depreciation schedule
        try:
            new_asset = await self.asset_depreciation_manager.create_asset_depreciation_schedule(new_asset)
        except Exception as e:
            # Log error but don't fail asset creation if depreciation schedule fails
            print(f"Warning: Failed to create depreciation schedule for asset {new_asset.asset_id}: {e}")

        return new_asset

    async def delete_asset(self, asset: AssetDTO) -> None:
        """
        Soft delete an asset (sets deleted flag)

        Args:
            asset: Asset to delete

        Raises:
            Exception: If deletion fails
        """
        try:
            await self.asset_db_context.delete_asset_async(asset)
        except Exception as e:
            raise Exception(f"Error deleting asset {asset.asset_id}: {e}")

    async def update_asset(self, asset: AssetDTO) -> Optional[AssetDTO]:
        """
        Update an existing asset with new valuation

        Args:
            asset: Updated asset data

        Returns:
            Updated asset with new valuation and depreciation schedule
        """
        # Update the asset in database
        updated_asset = await self.asset_db_context.update_asset_async(asset)

        # Get updated valuation from external API
        try:
            if asset.type == "Equipment":
                equipment_valuation = await self.asset_valuation_service.get_equipment_valuation_async(
                    asset.manufacturer,
                    asset.model,
                    asset.model_year,
                    str(asset.usage),
                    asset.condition,
                    asset.country,
                    asset.state
                )

                await self.valuation_db_context.insert_equipment_valuation_async(
                    equipment_valuation,
                    asset.asset_id
                )

                updated_asset.fair_market_values_over_time = [
                    FairMarketValueDTO(
                        time_set=datetime.now(),
                        value=equipment_valuation.adjusted_forced_liquidation_value or 0.0
                    )
                ]

            elif asset.type == "Vehicle":
                vehicle_valuation = await self.asset_valuation_service.get_vehicle_valuation_async(
                    asset.manufacturer,
                    asset.model,
                    asset.model_year,
                    str(asset.usage),
                    asset.condition,
                    asset.country,
                    asset.state
                )

                await self.valuation_db_context.insert_vehicle_valuation_async(
                    vehicle_valuation,
                    asset.asset_id
                )

                updated_asset.fair_market_values_over_time = [
                    FairMarketValueDTO(
                        time_set=datetime.now(),
                        value=vehicle_valuation.adjusted_trade_in or 0.0
                    )
                ]
        except Exception as e:
            # Log error but don't fail asset update if valuation fails
            print(f"Warning: Failed to fetch valuation for asset {asset.asset_id}: {e}")

        # Update depreciation schedule
        try:
            updated_asset = await self.asset_depreciation_manager.update_asset_depreciation_record(updated_asset)
        except Exception as e:
            # Log error but don't fail asset update if depreciation schedule update fails
            print(f"Warning: Failed to update depreciation schedule for asset {asset.asset_id}: {e}")

        return updated_asset
