from fastapi import APIRouter, HTTPException, status, Body
from typing import List
from models.asset_models import AssetDTO
from managers.asset_manager import AssetManager
import logging

router = APIRouter()

# Initialize manager
asset_manager = AssetManager()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/GetAssets")
async def get_user_assets(user_id: int = Body(..., embed=True)):
    """
    Get all assets for a user

    Args:
        user_id: User ID (from request body to match C# implementation)

    Returns:
        List of assets
    """
    try:
        assets = await asset_manager.get_assets(user_id)

        if assets is not None:
            return assets
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No equipment data found."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"An error occurred while getting assets for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)}
        )


@router.post("/CreateAsset")
async def create_asset(asset: AssetDTO):
    """
    Create a new asset

    Args:
        asset: Asset data

    Returns:
        Created asset with message
    """
    try:
        new_asset = await asset_manager.create_asset(asset)

        if new_asset is not None:
            return {
                "asset": new_asset,
                "message": "Asset created successfully."
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create asset."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"An error occurred while creating asset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)}
        )


@router.put("/DeleteAsset")
async def delete_asset(asset: AssetDTO):
    """
    Soft delete an asset (sets deleted flag to TRUE)

    Args:
        asset: Asset to delete

    Returns:
        Success message
    """
    try:
        await asset_manager.delete_asset(asset)
        return {"message": "The asset was deleted successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)}
        )


@router.put("/UpdateAsset")
async def update_asset(asset: AssetDTO):
    """
    Update an existing asset

    Args:
        asset: Updated asset data

    Returns:
        Updated asset with message
    """
    try:
        updated_asset = await asset_manager.update_asset(asset)

        if updated_asset is not None:
            return {
                "updatedAsset": updated_asset,
                "message": "Asset updated successfully."
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update asset."
            )

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )
