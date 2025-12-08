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
    book_value: float = Field(alias="BookValue")
    manufacturer: str = Field(alias="Manufacturer")
    model: str = Field(alias="Model")
    model_year: str = Field(alias="ModelYear")
    usage: int = Field(alias="Usage")
    condition: str = Field(alias="Condition")
    country: str = Field(alias="Country")
    state: str = Field(alias="State")
    deleted: bool = Field(default=False, alias="Deleted")
    depreciation_method: str = Field(alias="DepreciationMethod")
    salvage_value: float = Field(alias="SalvageValue")
    useful_life: Optional[int] = Field(default=None, alias="UsefulLife")
    depreciation_rate: Optional[float] = Field(default=None, alias="DepreciationRate")
    total_expected_units_of_production: Optional[int] = Field(default=None, alias="TotalExpectedUnitsOfProduction")
    units_produced_in_year: Optional[int] = Field(default=None, alias="UnitsProducedInYear")
    create_date: Optional[str] = Field(default=None, alias="CreateDate")
    update_date: Optional[str] = Field(default=None, alias="UpdateDate")
    fair_market_values_over_time: List[FairMarketValueDTO] = Field(default_factory=list, alias="fairMarketValuesOverTime")
    asset_depreciation_schedule: List[AssetDepreciationDTO] = Field(default_factory=list, alias="assetDepreciationSchedule")

    class Config:
        populate_by_name = True
        from_attributes = True
