"""
Pydantic models for Scenario API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============================================================
# REQUEST MODELS
# ============================================================

class AssetSaleRequest(BaseModel):
    """Asset being liquidated"""
    asset_id: int = Field(alias="assetId")
    asset_name: str = Field(alias="assetName")
    original_cost: float = Field(alias="originalCost")
    accumulated_depreciation: float = Field(alias="accumulatedDepreciation")
    sale_price: float = Field(alias="salePrice")
    transaction_fees: float = Field(default=0.0, alias="transactionFees")
    close_month: str = Field(alias="closeMonth")  # YYYY-MM
    
    class Config:
        populate_by_name = True


class ReplacementAssetRequest(BaseModel):
    """Replacement asset being purchased"""
    name: str
    cost: float
    method: str  # "BONUS", "SECTION_179", "MACRS_GDS", "MACRS_ADS"
    business_use_percent: float = Field(alias="businessUsePercent")
    in_service_month: str = Field(alias="inServiceMonth")  # YYYY-MM
    useful_life: int = Field(default=5, alias="usefulLife")
    
    class Config:
        populate_by_name = True


class ScenarioCalculationRequest(BaseModel):
    """Complete scenario calculation request"""
    user_id: int = Field(alias="userId")
    assets_to_sell: List[AssetSaleRequest] = Field(alias="assetsToSell")
    replacement_assets: List[ReplacementAssetRequest] = Field(alias="replacementAssets")
    
    # Tax settings
    marginal_tax_rate: float = Field(alias="marginalTaxRate")  # decimal (e.g., 0.24)
    capital_gains_rate: float = Field(default=0.15, alias="capitalGainsRate")
    business_income_limit: Optional[float] = Field(default=None, alias="businessIncomeLimit")
    
    # Optional overrides
    override_section_179_limit: Optional[int] = Field(default=None, alias="overrideSection179Limit")
    override_bonus_percent: Optional[int] = Field(default=None, alias="overrideBonusPercent")
    
    class Config:
        populate_by_name = True


# ============================================================
# RESPONSE MODELS
# ============================================================

class SaleDetailResponse(BaseModel):
    """Individual asset sale breakdown"""
    asset_name: str = Field(alias="assetName")
    sale_price: float = Field(alias="salePrice")
    original_cost: float = Field(alias="originalCost")
    accumulated_depreciation: float = Field(alias="accumulatedDepreciation")
    adjusted_basis: float = Field(alias="adjustedBasis")
    total_gain: float = Field(alias="totalGain")
    section_1245_recapture: float = Field(alias="section1245Recapture")
    section_1231_gain: float = Field(alias="section1231Gain")
    transaction_fees: float = Field(alias="transactionFees")
    tax_on_recapture: float = Field(alias="taxOnRecapture")
    tax_on_capital_gain: float = Field(alias="taxOnCapitalGain")
    net_proceeds_after_tax: float = Field(alias="netProceedsAfterTax")
    notes: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


class ReplacementDetailResponse(BaseModel):
    """Individual replacement depreciation breakdown"""
    asset_name: str = Field(alias="assetName")
    cost: float
    business_use_percent: float = Field(alias="businessUsePercent")
    depreciable_basis: float = Field(alias="depreciableBasis")
    bonus_depreciation: float = Field(alias="bonusDepreciation")
    section_179_deduction: float = Field(alias="section179Deduction")
    macrs_first_year: float = Field(alias="macrsFirstYear")
    total_first_year_deduction: float = Field(alias="totalFirstYearDeduction")
    remaining_basis: float = Field(alias="remainingBasis")
    method_used: str = Field(alias="methodUsed")
    notes: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


class ScenarioResultsResponse(BaseModel):
    """Complete scenario calculation results"""
    
    # Liquidation summary
    total_sale_proceeds: float = Field(alias="totalSaleProceeds")
    total_transaction_fees: float = Field(alias="totalTransactionFees")
    total_section_1245_recapture: float = Field(alias="totalSection1245Recapture")
    total_section_1231_gain: float = Field(alias="totalSection1231Gain")
    total_tax_on_sales: float = Field(alias="totalTaxOnSales")
    net_cash_from_liquidation: float = Field(alias="netCashFromLiquidation")
    
    # Replacement summary
    total_replacement_cost: float = Field(alias="totalReplacementCost")
    total_bonus_depreciation: float = Field(alias="totalBonusDepreciation")
    total_section_179: float = Field(alias="totalSection179")
    total_macrs_first_year: float = Field(alias="totalMacrsFirstYear")
    total_first_year_deductions: float = Field(alias="totalFirstYearDeductions")
    tax_savings_from_deductions: float = Field(alias="taxSavingsFromDeductions")
    
    # Net cash analysis
    cash_required_for_replacements: float = Field(alias="cashRequiredForReplacements")
    net_cash_flow: float = Field(alias="netCashFlow")
    
    # Detailed breakdowns
    sale_details: List[SaleDetailResponse] = Field(alias="saleDetails")
    replacement_details: List[ReplacementDetailResponse] = Field(alias="replacementDetails")
    
    # Metadata
    calculated_at: datetime = Field(alias="calculatedAt")
    tax_year: int = Field(alias="taxYear")
    warnings: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


# ============================================================
# TAX POLICY INFO RESPONSES
# ============================================================

class TaxPolicyResponse(BaseModel):
    """Tax policy information for a given year"""
    effective_year: int = Field(alias="effectiveYear")
    section_179_limit: int = Field(alias="section179Limit")
    section_179_phaseout_threshold: int = Field(alias="section179PhaseoutThreshold")
    bonus_depreciation_percent: int = Field(alias="bonusDepreciationPercent")
    policy_source: str = Field(alias="policySource")
    
    class Config:
        populate_by_name = True