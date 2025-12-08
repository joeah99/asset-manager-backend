from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EquipmentValuationDTO(BaseModel):
    """Equipment valuation data from EquipmentWatch API"""
    log_id: int = Field(default=0, alias="LogId")
    asset_id: int = Field(default=0, alias="AssetId")
    unadjusted_fair_market_value: Optional[float] = Field(default=None, alias="unadjustedFmv")
    unadjusted_orderly_liquidation_value: Optional[float] = Field(default=None, alias="unadjustedOlv")
    unadjusted_forced_liquidation_value: Optional[float] = Field(default=None, alias="unadjustedFlv")
    adjusted_fair_market_value: Optional[float] = Field(default=None, alias="adjustedFmv")
    adjusted_orderly_liquidation_value: Optional[float] = Field(default=None, alias="adjustedOlv")
    adjusted_forced_liquidation_value: Optional[float] = Field(default=None, alias="adjustedFlv")
    salvage: Optional[float] = Field(default=None, alias="salvage")
    valuation_date: Optional[datetime] = Field(default=None, alias="ValuationDate")

    class Config:
        populate_by_name = True


class VehicleValuationDTO(BaseModel):
    """Vehicle valuation data from PriceDigest API"""
    log_id: int = Field(default=0, alias="LogId")
    asset_id: int = Field(default=0, alias="AssetId")
    unadjusted_low: Optional[float] = Field(default=None, alias="unadjustedLow")
    unadjusted_high: Optional[float] = Field(default=None, alias="unadjustedHigh")
    unadjusted_finance: Optional[float] = Field(default=None, alias="unadjustedFinance")
    unadjusted_retail: Optional[float] = Field(default=None, alias="unadjustedRetail")
    unadjusted_wholesale: Optional[float] = Field(default=None, alias="unadjustedWholesale")
    unadjusted_trade_in: Optional[float] = Field(default=None, alias="unadjustedTradeIn")
    adjusted_low: Optional[float] = Field(default=None, alias="adjustedLow")
    adjusted_high: Optional[float] = Field(default=None, alias="adjustedHigh")
    adjusted_finance: Optional[float] = Field(default=None, alias="adjustedFinance")
    adjusted_retail: Optional[float] = Field(default=None, alias="adjustedRetail")
    adjusted_wholesale: Optional[float] = Field(default=None, alias="adjustedWholesale")
    adjusted_trade_in: Optional[float] = Field(default=None, alias="adjustedTradeIn")
    valuation_date: Optional[datetime] = Field(default=None, alias="ValuationDate")

    class Config:
        populate_by_name = True


class MonthlyTotalFMVDTO(BaseModel):
    """Monthly aggregated fair market value"""
    month: str = Field(alias="Month")
    total_fair_market_value: float = Field(alias="TotalFairMarketValue")
    number_of_assets: int = Field(alias="NumberOfAssets")

    class Config:
        populate_by_name = True


class TotalAssetValueDTO(BaseModel):
    """Total asset value with year-over-year change"""
    total_asset_value: float = Field(alias="TotalAssetValue")
    percent_change_past_year: int = Field(alias="percentChangePastYear")

    class Config:
        populate_by_name = True


class AdjustedForcedLiquidationDTO(BaseModel):
    """Adjusted forced liquidation value for an asset"""
    asset_id: int = Field(alias="AssetId")
    valuation_date: str = Field(alias="ValuationDate")
    adjusted_forced_liquidation_value: Optional[float] = Field(alias="AdjustedForcedLiquidationValue")

    class Config:
        populate_by_name = True


class AdjustedForcedLiquidation(BaseModel):
    """Internal model for database operations"""
    asset_id: int
    valuation_date: datetime
    adjusted_forced_liquidation_value: Optional[float]
