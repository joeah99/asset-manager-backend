from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FairMarketValueDTO(BaseModel):
    """Fair market value at a specific time"""
    time_set: datetime = Field(alias="timeSet")
    value: float

    class Config:
        populate_by_name = True


class AssetDepreciationDTO(BaseModel):
    """Asset depreciation entry"""
    depreciation_date: str = Field(alias="DepreciationDate")
    new_book_value: float = Field(alias="NewBookValue")

    class Config:
        populate_by_name = True


class AssetDepreciationScheduleDTO(BaseModel):
    """Full asset depreciation schedule entry with database fields"""
    asset_depreciation_schedule_id: int = Field(default=0, alias="AssetDepreciationScheduleId")
    asset_id: int = Field(alias="AssetId")
    depreciation_date: str = Field(alias="DepreciationDate")
    new_book_value: float = Field(alias="NewBookValue")
    created_at: datetime = Field(alias="CreatedAt")

    class Config:
        populate_by_name = True


class DepreciationScheduleWithIdDTO(BaseModel):
    """Depreciation schedule entry with asset ID"""
    asset_id: int = Field(alias="AssetId")
    depreciation_date: str = Field(alias="DepreciationDate")
    new_book_value: Optional[float] = Field(alias="NewBookValue")

    class Config:
        populate_by_name = True


class AssetDTO(BaseModel):
    """Asset model with all fields"""
    asset_id: int = Field(default=0, alias="AssetId")
    user_id: int = Field(alias="UserId")
    type: str = Field(alias="Type")  # "Equipment" or "Vehicle"
    purchase_price: float = Field(default=0.0, alias="PurchasePrice")
    purchase_date: Optional[str] = Field(default=None, alias="PurchaseDate")
    book_value: float = Field(alias="BookValue")
    manufacturer: str = Field(alias="Manufacturer")
    model: str = Field(alias="Model")
    model_year: str = Field(alias="ModelYear")
    usage: int = Field(alias="Usage")
    usage_unit: str = Field(default="hours", alias="UsageUnit")
    condition: str = Field(alias="Condition")
    country: str = Field(alias="Country")
    zip_code: Optional[str] = Field(default=None, alias="ZipCode")
    depreciation_method: str = Field(alias="DepreciationMethod")
    useful_life: Optional[int] = Field(default=None, alias="UsefulLife")
    create_date: Optional[str] = Field(default=None, alias="CreateDate")
    update_date: Optional[str] = Field(default=None, alias="UpdateDate")
    fmv: Optional[float] = Field(default=0.0, alias="FMV")
    fair_market_values_over_time: List[FairMarketValueDTO] = Field(default_factory=list, alias="fairMarketValuesOverTime")
    asset_depreciation_schedule: List[AssetDepreciationDTO] = Field(default_factory=list, alias="assetDepreciationSchedule")

    class Config:
        populate_by_name = True
        from_attributes = True
