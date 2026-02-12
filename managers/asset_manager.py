from typing import List, Optional
from datetime import datetime
from models.asset_models import AssetDTO, FairMarketValueDTO
from db.asset_db import AssetDbContext


class AssetManager:
    """
    Manager for asset operations (equivalent to C# AssetManager)
    Integrates asset CRUD with valuations and depreciation
    """

    def __init__(
        self,
        asset_db_context: AssetDbContext = None
    ):
        self.asset_db_context = asset_db_context or AssetDbContext()

    async def get_assets(self, user_id: int) -> List[AssetDTO]:
        """
        Get all assets for a user

        Args:
            user_id: User ID

        Returns:
            List of assets
        """
        # Get assets from database
        asset_list = await self.asset_db_context.get_assets_async(user_id)
        
        # Note: Valuation and Legacy Depreciation schedules are no longer populated here.
        # They will default to empty lists in the DTO if not populated.

        return asset_list

    async def create_asset(self, asset: AssetDTO) -> Optional[AssetDTO]:
        """
        Create a new asset

        Args:
            asset: Asset data

        Returns:
            Created asset
        """
        # Check if asset already exists
        existing_asset = await self.asset_db_context.get_asset_async(asset.user_id, asset)

        if existing_asset:
            return None  # Asset already exists

        # Create the asset
        new_asset = await self.asset_db_context.create_asset_async(asset)
        
        # Initialize empty lists for compatibility
        new_asset.fair_market_values_over_time = []
        new_asset.asset_depreciation_schedule = []

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
        Update an existing asset

        Args:
            asset: Updated asset data

        Returns:
            Updated asset
        """
        # Update the asset in database
        updated_asset = await self.asset_db_context.update_asset_async(asset)
        
        # Initialize empty lists for compatibility if needed
        if updated_asset:
            updated_asset.fair_market_values_over_time = []
            updated_asset.asset_depreciation_schedule = []

        return updated_asset
