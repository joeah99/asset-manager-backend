"""
Scenario Calculation Service - Main Orchestrator

Coordinates liquidation, replacement, and tax calculations.
This is the main service that the API endpoint will call.
"""

from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from services.tax_policy_service import TaxPolicyService
from services.depreciation_calculation_service import (
    DepreciationCalculationService,
    DepreciationCalculation
)
from services.basis_recapture_service import (
    BasisRecaptureService,
    SaleCalculation
)


@dataclass
class AssetSale:
    """Input: Asset being sold"""
    asset_id: int
    asset_name: str
    original_cost: float
    accumulated_depreciation: float  # From DB or estimated
    sale_price: float
    transaction_fees: float
    close_month: str  # YYYY-MM format


@dataclass
class ReplacementAsset:
    """Input: Replacement asset being purchased"""
    name: str
    cost: float
    method: str  # "BONUS", "SECTION_179", "MACRS_GDS", "MACRS_ADS"
    business_use_percent: float  # 0-100
    in_service_month: str  # YYYY-MM format
    useful_life: int = 5  # MACRS class life


@dataclass
class ScenarioInputs:
    """Complete scenario inputs from user"""
    user_id: int
    assets_to_sell: List[AssetSale]
    replacement_assets: List[ReplacementAsset]
    
    # Tax settings
    marginal_tax_rate: float  # e.g., 0.24 for 24%
    capital_gains_rate: float = 0.15  # Long-term cap gains
    business_income_limit: Optional[float] = None  # For §179 limitation
    
    # Optional overrides
    override_section_179_limit: Optional[int] = None
    override_bonus_percent: Optional[int] = None


@dataclass
class ScenarioResults:
    """Complete scenario calculation results"""
    
    # Liquidation summary
    total_sale_proceeds: float = 0.0
    total_transaction_fees: float = 0.0
    total_section_1245_recapture: float = 0.0
    total_section_1231_gain: float = 0.0
    total_tax_on_sales: float = 0.0
    net_cash_from_liquidation: float = 0.0
    
    # Replacement summary
    total_replacement_cost: float = 0.0
    total_bonus_depreciation: float = 0.0
    total_section_179: float = 0.0
    total_macrs_first_year: float = 0.0
    total_first_year_deductions: float = 0.0
    tax_savings_from_deductions: float = 0.0
    
    # Net cash analysis
    cash_required_for_replacements: float = 0.0
    net_cash_flow: float = 0.0  # liquidation proceeds - replacement cost + tax savings
    
    # Detailed breakdowns
    sale_details: List[SaleCalculation] = field(default_factory=list)
    replacement_details: List[DepreciationCalculation] = field(default_factory=list)
    
    # Metadata
    calculated_at: datetime = field(default_factory=datetime.now)
    tax_year: int = field(default_factory=lambda: datetime.now().year)
    warnings: List[str] = field(default_factory=list)


class ScenarioCalculationService:
    """
    Main orchestrator for scenario calculations.
    
    Coordinates:
    1. Liquidation tax impact (§1245 recapture, §1231 gains)
    2. Replacement depreciation (Bonus, §179, MACRS)
    3. Net cash flow analysis
    4. Tax savings calculation
    """
    
    def __init__(
        self,
        tax_policy_service: TaxPolicyService = None,
        depreciation_service: DepreciationCalculationService = None,
        basis_service: BasisRecaptureService = None
    ):
        self.tax_policy_service = tax_policy_service or TaxPolicyService()
        self.depreciation_service = depreciation_service or DepreciationCalculationService(
            self.tax_policy_service
        )
        self.basis_service = basis_service or BasisRecaptureService()
    
    def calculate_scenario(self, inputs: ScenarioInputs) -> ScenarioResults:
        """
        Calculate complete scenario with liquidations and replacements.
        
        Args:
            inputs: Complete scenario inputs
            
        Returns:
            ScenarioResults with full analysis
        """
        results = ScenarioResults()
        
        # Step 1: Calculate liquidation impact
        for sale in inputs.assets_to_sell:
            sale_calc = self.basis_service.calculate_sale_tax_impact(
                asset_name=sale.asset_name,
                original_cost=sale.original_cost,
                accumulated_depreciation=sale.accumulated_depreciation,
                sale_price=sale.sale_price,
                transaction_fees=sale.transaction_fees,
                ordinary_tax_rate=inputs.marginal_tax_rate,
                capital_gains_rate=inputs.capital_gains_rate,
                sale_date=self._parse_month(sale.close_month)
            )
            
            results.sale_details.append(sale_calc)
            results.total_sale_proceeds += sale_calc.gross_proceeds
            results.total_transaction_fees += sale_calc.transaction_fees
            results.total_section_1245_recapture += sale_calc.section_1245_recapture
            results.total_section_1231_gain += sale_calc.section_1231_gain
            results.total_tax_on_sales += (sale_calc.tax_on_recapture + sale_calc.tax_on_capital_gain)
        
        results.net_cash_from_liquidation = (
            results.total_sale_proceeds 
            - results.total_transaction_fees 
            - results.total_tax_on_sales
        )
        
        # Step 2: Calculate replacement depreciation
        # Determine §179 budget and allocation
        tax_year = datetime.now().year
        policy = self.tax_policy_service.get_policy_for_year(tax_year)
        
        # Calculate total replacement purchases for phaseout
        total_replacement_cost = sum(r.cost for r in inputs.replacement_assets)
        results.total_replacement_cost = total_replacement_cost
        
        # Get §179 limit with phaseout
        if inputs.override_section_179_limit is not None:
            section_179_budget = inputs.override_section_179_limit
        else:
            section_179_budget = self.tax_policy_service.calculate_section_179_limit_with_phaseout(
                total_replacement_cost,
                tax_year
            )
        
        section_179_remaining = float(section_179_budget)
        
        # Process each replacement
        for replacement in inputs.replacement_assets:
            in_service_date = self._parse_month(replacement.in_service_month)
            
            if replacement.method == "BONUS":
                depr_calc = self.depreciation_service.calculate_bonus_depreciation(
                    asset_name=replacement.name,
                    cost=replacement.cost,
                    business_use_percent=replacement.business_use_percent,
                    in_service_date=in_service_date,
                    override_bonus_percent=inputs.override_bonus_percent
                )
                results.total_bonus_depreciation += depr_calc.bonus_depreciation
                
            elif replacement.method == "SECTION_179":
                depr_calc = self.depreciation_service.calculate_section_179(
                    asset_name=replacement.name,
                    cost=replacement.cost,
                    business_use_percent=replacement.business_use_percent,
                    in_service_date=in_service_date,
                    section_179_available=section_179_remaining,
                    business_income_limit=inputs.business_income_limit
                )
                results.total_section_179 += depr_calc.section_179_deduction
                section_179_remaining -= depr_calc.section_179_deduction
                
            elif replacement.method == "MACRS_GDS":
                depr_calc = self.depreciation_service.calculate_macrs_gds(
                    asset_name=replacement.name,
                    cost=replacement.cost,
                    business_use_percent=replacement.business_use_percent,
                    in_service_date=in_service_date,
                    useful_life=replacement.useful_life
                )
                results.total_macrs_first_year += depr_calc.macrs_first_year
                
            elif replacement.method == "MACRS_ADS":
                depr_calc = self.depreciation_service.calculate_macrs_ads(
                    asset_name=replacement.name,
                    cost=replacement.cost,
                    business_use_percent=replacement.business_use_percent,
                    in_service_date=in_service_date,
                    useful_life=replacement.useful_life
                )
                results.total_macrs_first_year += depr_calc.macrs_first_year
                
            else:
                results.warnings.append(f"Unknown method '{replacement.method}' for {replacement.name}")
                continue
            
            results.replacement_details.append(depr_calc)
        
        # Step 3: Calculate tax savings from replacements
        results.total_first_year_deductions = (
            results.total_bonus_depreciation 
            + results.total_section_179 
            + results.total_macrs_first_year
        )
        
        results.tax_savings_from_deductions = (
            results.total_first_year_deductions * inputs.marginal_tax_rate
        )
        
        # Step 4: Net cash flow analysis
        results.cash_required_for_replacements = results.total_replacement_cost
        
        results.net_cash_flow = (
            results.net_cash_from_liquidation 
            + results.tax_savings_from_deductions 
            - results.cash_required_for_replacements
        )
        
        # Add warnings if applicable
        if section_179_remaining < section_179_budget:
            results.warnings.append(
                f"§179 limit reached. Used ${section_179_budget - section_179_remaining:,.0f} "
                f"of ${section_179_budget:,.0f} available."
            )
        
        if results.net_cash_flow < 0:
            results.warnings.append(
                f"Scenario requires additional cash: ${abs(results.net_cash_flow):,.2f}"
            )
        
        return results
    
    def _parse_month(self, month_str: str) -> datetime:
        """Parse YYYY-MM string to datetime (first day of month)"""
        try:
            return datetime.strptime(f"{month_str}-01", "%Y-%m-%d")
        except (ValueError, TypeError):
            return datetime.now()