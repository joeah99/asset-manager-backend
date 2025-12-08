"""
Scenario API Routes

Endpoints for scenario calculations, tax policy info, and depreciation analysis.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
import logging

from models.scenario_models import (
    ScenarioCalculationRequest,
    ScenarioResultsResponse,
    SaleDetailResponse,
    ReplacementDetailResponse,
    TaxPolicyResponse
)
from services.scenario_calculation_service import (
    ScenarioCalculationService,
    ScenarioInputs,
    AssetSale,
    ReplacementAsset
)
from services.tax_policy_service import TaxPolicyService

router = APIRouter()

# Initialize services
scenario_service = ScenarioCalculationService()
tax_policy_service = TaxPolicyService()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/calculate", response_model=ScenarioResultsResponse, name="CalculateScenario")
async def calculate_scenario(request: ScenarioCalculationRequest):
    """
    Calculate complete liquidation and replacement scenario.
    
    This endpoint orchestrates:
    1. Asset sale tax calculations (§1245 recapture, §1231 gains)
    2. Replacement depreciation (Bonus, §179, MACRS)
    3. Net cash flow analysis
    4. Tax savings computation
    
    Args:
        request: Complete scenario inputs
        
    Returns:
        Detailed scenario results with tax breakdown
    """
    try:
        logger.info(f"Calculating scenario for user {request.user_id}")
        
        # Convert request to service inputs
        assets_to_sell = [
            AssetSale(
                asset_id=sale.asset_id,
                asset_name=sale.asset_name,
                original_cost=sale.original_cost,
                accumulated_depreciation=sale.accumulated_depreciation,
                sale_price=sale.sale_price,
                transaction_fees=sale.transaction_fees,
                close_month=sale.close_month
            )
            for sale in request.assets_to_sell
        ]
        
        replacement_assets = [
            ReplacementAsset(
                name=repl.name,
                cost=repl.cost,
                method=repl.method,
                business_use_percent=repl.business_use_percent,
                in_service_month=repl.in_service_month,
                useful_life=repl.useful_life
            )
            for repl in request.replacement_assets
        ]
        
        inputs = ScenarioInputs(
            user_id=request.user_id,
            assets_to_sell=assets_to_sell,
            replacement_assets=replacement_assets,
            marginal_tax_rate=request.marginal_tax_rate,
            capital_gains_rate=request.capital_gains_rate,
            business_income_limit=request.business_income_limit,
            override_section_179_limit=request.override_section_179_limit,
            override_bonus_percent=request.override_bonus_percent
        )
        
        # Calculate scenario
        results = scenario_service.calculate_scenario(inputs)
        
        # Convert to response
        sale_details = [
            SaleDetailResponse(
                asset_name=sale.asset_name,
                sale_price=sale.sale_price,
                original_cost=sale.original_cost,
                accumulated_depreciation=sale.accumulated_depreciation,
                adjusted_basis=sale.adjusted_basis,
                total_gain=sale.total_gain,
                section_1245_recapture=sale.section_1245_recapture,
                section_1231_gain=sale.section_1231_gain,
                transaction_fees=sale.transaction_fees,
                tax_on_recapture=sale.tax_on_recapture,
                tax_on_capital_gain=sale.tax_on_capital_gain,
                net_proceeds_after_tax=sale.net_proceeds_after_tax,
                notes=sale.notes
            )
            for sale in results.sale_details
        ]
        
        replacement_details = [
            ReplacementDetailResponse(
                asset_name=repl.asset_name,
                cost=repl.cost,
                business_use_percent=repl.business_use_percent,
                depreciable_basis=repl.depreciable_basis,
                bonus_depreciation=repl.bonus_depreciation,
                section_179_deduction=repl.section_179_deduction,
                macrs_first_year=repl.macrs_first_year,
                total_first_year_deduction=repl.total_first_year_deduction,
                remaining_basis=repl.remaining_basis,
                method_used=repl.method_used,
                notes=repl.notes
            )
            for repl in results.replacement_details
        ]
        
        response = ScenarioResultsResponse(
            total_sale_proceeds=results.total_sale_proceeds,
            total_transaction_fees=results.total_transaction_fees,
            total_section_1245_recapture=results.total_section_1245_recapture,
            total_section_1231_gain=results.total_section_1231_gain,
            total_tax_on_sales=results.total_tax_on_sales,
            net_cash_from_liquidation=results.net_cash_from_liquidation,
            total_replacement_cost=results.total_replacement_cost,
            total_bonus_depreciation=results.total_bonus_depreciation,
            total_section_179=results.total_section_179,
            total_macrs_first_year=results.total_macrs_first_year,
            total_first_year_deductions=results.total_first_year_deductions,
            tax_savings_from_deductions=results.tax_savings_from_deductions,
            cash_required_for_replacements=results.cash_required_for_replacements,
            net_cash_flow=results.net_cash_flow,
            sale_details=sale_details,
            replacement_details=replacement_details,
            calculated_at=results.calculated_at,
            tax_year=results.tax_year,
            warnings=results.warnings
        )
        
        logger.info(f"Scenario calculated successfully. Net cash flow: ${results.net_cash_flow:,.2f}")
        return response
        
    except Exception as e:
        logger.error(f"Error calculating scenario: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Error calculating scenario: {str(e)}"}
        )


@router.get("/tax-policy/{year}", response_model=TaxPolicyResponse, name="GetTaxPolicy")
async def get_tax_policy(year: int):
    """
    Get tax policy information for a specific year.
    
    Returns §179 limits, bonus depreciation rates, MACRS schedules, etc.
    
    Args:
        year: Tax year (e.g., 2024, 2025)
        
    Returns:
        Tax policy details
    """
    try:
        policy = tax_policy_service.get_policy_for_year(year)
        
        return TaxPolicyResponse(
            effective_year=policy.effective_year,
            section_179_limit=policy.section_179_limit,
            section_179_phaseout_threshold=policy.section_179_phaseout_threshold,
            bonus_depreciation_percent=policy.bonus_depreciation_percent,
            policy_source=policy.policy_source
        )
        
    except Exception as e:
        logger.error(f"Error fetching tax policy for {year}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Error fetching tax policy: {str(e)}"}
        )


@router.get("/tax-policy/current", response_model=TaxPolicyResponse, name="GetCurrentTaxPolicy")
async def get_current_tax_policy():
    """
    Get current year's tax policy information.
    
    Returns:
        Current tax policy details
    """
    from datetime import datetime
    return await get_tax_policy(datetime.now().year)


@router.get("/marginal-rate", name="GetMarginalRate")
async def get_marginal_rate(
    taxable_income: float = Query(..., description="Taxable income amount"),
    year: int = Query(default=2025, description="Tax year")
):
    """
    Calculate marginal tax rate for a given income level.
    
    Useful for helping users determine their tax rate for scenario inputs.
    
    Args:
        taxable_income: Taxable income amount
        year: Tax year
        
    Returns:
        Marginal rate information
    """
    try:
        rate = tax_policy_service.get_marginal_rate(taxable_income, year)
        
        return {
            "taxableIncome": taxable_income,
            "year": year,
            "marginalRate": rate,
            "marginalRatePercent": rate * 100
        }
        
    except Exception as e:
        logger.error(f"Error calculating marginal rate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Error calculating marginal rate: {str(e)}"}
        )


@router.post("/validate-inputs", name="ValidateScenarioInputs")
async def validate_scenario_inputs(request: ScenarioCalculationRequest):
    """
    Validate scenario inputs without performing full calculation.
    
    Useful for client-side validation before submitting scenario.
    
    Args:
        request: Scenario inputs to validate
        
    Returns:
        Validation results with any errors or warnings
    """
    errors = []
    warnings = []
    
    try:
        # Basic validations
        if not request.assets_to_sell and not request.replacement_assets:
            errors.append("Must include either assets to sell or replacement assets")
        
        if request.marginal_tax_rate < 0 or request.marginal_tax_rate > 1:
            errors.append("Marginal tax rate must be between 0 and 1")
        
        # Check §179 phaseout
        if request.replacement_assets:
            total_cost = sum(r.cost for r in request.replacement_assets)
            policy = tax_policy_service.get_policy_for_year(2025)
            
            if total_cost > policy.section_179_phaseout_threshold:
                warnings.append(
                    f"Total replacement cost (${total_cost:,.0f}) exceeds §179 phaseout "
                    f"threshold (${policy.section_179_phaseout_threshold:,}). "
                    f"§179 deduction will be reduced."
                )
        
        # Check for negative sale prices
        for sale in request.assets_to_sell:
            if sale.sale_price < 0:
                errors.append(f"Sale price for {sale.asset_name} cannot be negative")
        
        # Check business use percentages
        for repl in request.replacement_assets:
            if repl.business_use_percent < 0 or repl.business_use_percent > 100:
                errors.append(f"Business use for {repl.name} must be between 0 and 100")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
    except Exception as e:
        logger.error(f"Error validating inputs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Error validating inputs: {str(e)}"}
        )