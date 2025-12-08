from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from models.valuation_models import (
    EquipmentValuationDTO,
    MonthlyTotalFMVDTO,
    TotalAssetValueDTO,
    AdjustedForcedLiquidationDTO
)
from managers.valuation_manager import ValuationManager
import logging

router = APIRouter()

# Initialize manager
valuation_manager = ValuationManager()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/", name="GetAssetValuations")
async def get_asset_valuations(user_id: int = Query(..., description="User ID")):
    """
    Get all equipment valuations for a user

    Args:
        user_id: User ID (query parameter)

    Returns:
        List of equipment valuations
    """
    try:
        valuations = await valuation_manager.get_equipment_valuations(user_id)

        if valuations is not None:
            return valuations
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No equipment valuation data found."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching valuations for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)}
        )


@router.get("/total-fmv", name="GetTotalFairMarketValue")
async def get_total_fair_market_value(user_id: int = Query(..., description="User ID")):
    """
    Get total fair market value aggregated by month for the last 12 months

    Args:
        user_id: User ID (query parameter)

    Returns:
        List of monthly FMV totals
    """
    try:
        total_fmv = await valuation_manager.get_total_fair_market_value(user_id)

        if total_fmv is not None:
            return total_fmv
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No total fair market value data found."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching total FMV for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)}
        )


@router.get("/total-Asset-Value")
async def get_total_asset_value(user_id: int = Query(..., description="User ID")):
    """
    Get total asset value with year-over-year percent change

    Args:
        user_id: User ID (query parameter)

    Returns:
        Total asset value and percent change
    """
    try:
        total_asset_value = await valuation_manager.get_total_asset_value(user_id)

        if total_asset_value is not None:
            return total_asset_value
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No total asset value data found."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching total asset value for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)}
        )


@router.get("/adjusted-forced-liquidation")
async def get_adjusted_forced_liquidation(user_id: int = Query(..., description="User ID")):
    """
    Get adjusted forced liquidation values for all user assets

    Args:
        user_id: User ID (query parameter)

    Returns:
        List of adjusted forced liquidation values
    """
    try:
        adjusted_forced_liquidation = await valuation_manager.get_adjusted_forced_liquidation_async(user_id)

        if adjusted_forced_liquidation is not None:
            return adjusted_forced_liquidation
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No adjusted forced liquidation data found."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching adjusted forced liquidation for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)}
        )
