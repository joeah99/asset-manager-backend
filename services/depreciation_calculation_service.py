"""
Depreciation Calculation Service

Handles Bonus Depreciation, §179 expensing, MACRS GDS/ADS calculations.
Integrates with TaxPolicyService for versioned rules.
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from services.tax_policy_service import TaxPolicyService


@dataclass
class DepreciationCalculation:
    """Result of depreciation calculation for a single asset"""
    asset_name: str
    cost: float
    business_use_percent: float
    depreciable_basis: float  # cost * business_use
    
    # Depreciation breakdown
    bonus_depreciation: float = 0.0
    section_179_deduction: float = 0.0
    macrs_first_year: float = 0.0
    
    # Total first-year deduction
    total_first_year_deduction: float = 0.0
    
    # Remaining basis for future years
    remaining_basis: float = 0.0
    
    method_used: str = ""
    in_service_date: Optional[datetime] = None
    notes: List[str] = None
    
    def __post_init__(self):
        if self.notes is None:
            self.notes = []


class DepreciationCalculationService:
    """
    Service for calculating depreciation under various methods.
    
    Supports:
    - Bonus Depreciation (60% in 2024, 40% in 2025, phasing to 0%)
    - §179 Expensing (with phaseout and business income limitation)
    - MACRS GDS (accelerated)
    - MACRS ADS (straight-line alternative)
    """
    
    def __init__(self, tax_policy_service: TaxPolicyService = None):
        self.tax_policy_service = tax_policy_service or TaxPolicyService()
    
    def calculate_bonus_depreciation(
        self,
        asset_name: str,
        cost: float,
        business_use_percent: float,
        in_service_date: datetime,
        override_bonus_percent: Optional[int] = None
    ) -> DepreciationCalculation:
        """
        Calculate bonus depreciation (immediate expensing).
        
        Bonus depreciation allows immediate deduction of a percentage
        of the asset's cost (phasing down from 100% to 0% by 2027).
        
        Args:
            asset_name: Asset identifier
            cost: Purchase cost
            business_use_percent: Business use percentage (0-100)
            in_service_date: Date asset was placed in service
            override_bonus_percent: Override policy bonus % (for user control)
            
        Returns:
            DepreciationCalculation with bonus amount
        """
        policy = self.tax_policy_service.get_policy_for_date(in_service_date)
        bonus_percent = override_bonus_percent if override_bonus_percent is not None else policy.bonus_depreciation_percent
        
        # Check Business Use threshold (> 50% required for Bonus)
        if business_use_percent <= 50.0:
            result = DepreciationCalculation(
                asset_name=asset_name,
                cost=cost,
                business_use_percent=business_use_percent,
                depreciable_basis=cost * (business_use_percent / 100.0),
                bonus_depreciation=0.0,
                total_first_year_deduction=0.0,
                remaining_basis=cost * (business_use_percent / 100.0),
                method_used="BONUS_INELIGIBLE",
                in_service_date=in_service_date
            )
            result.notes.append("Bonus Depreciation not available: Business use is 50% or less.")
            return result
        
        # Calculate depreciable basis
        depreciable_basis = cost * (business_use_percent / 100.0)
        
        # Bonus depreciation
        bonus_amount = depreciable_basis * (bonus_percent / 100.0)
        remaining_basis = depreciable_basis - bonus_amount
        
        result = DepreciationCalculation(
            asset_name=asset_name,
            cost=cost,
            business_use_percent=business_use_percent,
            depreciable_basis=depreciable_basis,
            bonus_depreciation=bonus_amount,
            total_first_year_deduction=bonus_amount,
            remaining_basis=remaining_basis,
            method_used="BONUS",
            in_service_date=in_service_date
        )
        
        result.notes.append(f"Bonus depreciation: {bonus_percent}% of ${depreciable_basis:,.2f}")
        
        return result
    
    def calculate_section_179(
        self,
        asset_name: str,
        cost: float,
        business_use_percent: float,
        in_service_date: datetime,
        section_179_available: float,  # Remaining §179 budget for the year
        business_income_limit: Optional[float] = None
    ) -> DepreciationCalculation:
        """
        Calculate §179 expensing.
        
        §179 allows immediate deduction up to annual limit ($1.22M in 2024),
        but cannot exceed business income and phases out with total purchases.
        
        Args:
            asset_name: Asset identifier
            cost: Purchase cost
            business_use_percent: Business use percentage
            in_service_date: Date placed in service
            section_179_available: Remaining §179 budget (after other assets)
            business_income_limit: Business income limit (§179 can't create loss)
            
        Returns:
            DepreciationCalculation with §179 amount
        """
        depreciable_basis = cost * (business_use_percent / 100.0)
        
        # Check Business Use threshold (> 50% required for §179)
        if business_use_percent <= 50.0:
            result = DepreciationCalculation(
                asset_name=asset_name,
                cost=cost,
                business_use_percent=business_use_percent,
                depreciable_basis=depreciable_basis,
                section_179_deduction=0.0,
                total_first_year_deduction=0.0,
                remaining_basis=depreciable_basis,
                method_used="SECTION_179_INELIGIBLE",
                in_service_date=in_service_date
            )
            result.notes.append("Section 179 not available: Business use is 50% or less.")
            return result

        policy = self.tax_policy_service.get_policy_for_date(in_service_date)
        
        # §179 limited by available budget
        section_179_amount = min(depreciable_basis, section_179_available)
        
        # Further limited by business income (can't create loss)
        if business_income_limit is not None:
            section_179_amount = min(section_179_amount, business_income_limit)
        
        remaining_basis = depreciable_basis - section_179_amount
        
        result = DepreciationCalculation(
            asset_name=asset_name,
            cost=cost,
            business_use_percent=business_use_percent,
            depreciable_basis=depreciable_basis,
            section_179_deduction=section_179_amount,
            total_first_year_deduction=section_179_amount,
            remaining_basis=remaining_basis,
            method_used="SECTION_179",
            in_service_date=in_service_date
        )
        
        result.notes.append(f"§179 deduction: ${section_179_amount:,.2f}")
        if section_179_amount < depreciable_basis:
            result.notes.append(f"Limited by available §179 budget: ${section_179_available:,.2f}")
        
        return result
    
    def calculate_macrs_gds(
        self,
        asset_name: str,
        cost: float,
        business_use_percent: float,
        in_service_date: datetime,
        useful_life: int = 5  # 5 or 7 years typical for equipment
    ) -> DepreciationCalculation:
        """
        Calculate MACRS GDS (accelerated depreciation).
        
        Uses IRS MACRS tables (e.g., 5-year property = 20%, 32%, 19.2%, ...)
        
        Args:
            asset_name: Asset identifier
            cost: Purchase cost
            business_use_percent: Business use percentage
            in_service_date: Date placed in service
            useful_life: MACRS class life (5 or 7 years)
            
        Returns:
            DepreciationCalculation with first-year MACRS
        """
        policy = self.tax_policy_service.get_policy_for_date(in_service_date)
        depreciable_basis = cost * (business_use_percent / 100.0)
        
        # Check Business Use threshold (> 50% required for GDS, else ADS)
        if business_use_percent <= 50.0:
             # If called directly, we return 0 and note that ADS is required
             result = DepreciationCalculation(
                asset_name=asset_name,
                cost=cost,
                business_use_percent=business_use_percent,
                depreciable_basis=depreciable_basis,
                macrs_first_year=0.0,
                total_first_year_deduction=0.0,
                remaining_basis=depreciable_basis,
                method_used="MACRS_GDS_INELIGIBLE",
                in_service_date=in_service_date
            )
             result.notes.append("MACRS GDS not available: Business use is 50% or less. Use MACRS ADS.")
             return result
        
        # Get first-year rate from policy
        first_year_rate = self.tax_policy_service.get_macrs_first_year_rate(useful_life, in_service_date.year)
        
        macrs_first_year = depreciable_basis * first_year_rate
        remaining_basis = depreciable_basis - macrs_first_year
        
        result = DepreciationCalculation(
            asset_name=asset_name,
            cost=cost,
            business_use_percent=business_use_percent,
            depreciable_basis=depreciable_basis,
            macrs_first_year=macrs_first_year,
            total_first_year_deduction=macrs_first_year,
            remaining_basis=remaining_basis,
            method_used="MACRS_GDS",
            in_service_date=in_service_date
        )
        
        result.notes.append(f"MACRS {useful_life}-year GDS: {first_year_rate*100:.2f}% first year")
        
        return result
    
    def calculate_macrs_ads(
        self,
        asset_name: str,
        cost: float,
        business_use_percent: float,
        in_service_date: datetime,
        useful_life: int = 5
    ) -> DepreciationCalculation:
        """
        Calculate MACRS ADS (straight-line alternative).
        
        ADS uses straight-line depreciation over longer recovery periods.
        For 5-year property, it's actually 6 years (half-year convention).
        
        Args:
            asset_name: Asset identifier
            cost: Purchase cost
            business_use_percent: Business use percentage
            in_service_date: Date placed in service
            useful_life: MACRS class life
            
        Returns:
            DepreciationCalculation with first-year ADS
        """
        depreciable_basis = cost * (business_use_percent / 100.0)
        
        # ADS straight-line with half-year convention
        # First year = (1 / useful_life) * 0.5
        ads_rate = (1.0 / useful_life) * 0.5
        ads_first_year = depreciable_basis * ads_rate
        remaining_basis = depreciable_basis - ads_first_year
        
        result = DepreciationCalculation(
            asset_name=asset_name,
            cost=cost,
            business_use_percent=business_use_percent,
            depreciable_basis=depreciable_basis,
            macrs_first_year=ads_first_year,  # Store in macrs_first_year field
            total_first_year_deduction=ads_first_year,
            remaining_basis=remaining_basis,
            method_used="MACRS_ADS",
            in_service_date=in_service_date
        )
        
        result.notes.append(f"MACRS ADS straight-line: {ads_rate*100:.2f}% first year")
        
        return result
    
    def calculate_optimal_method(
        self,
        asset_name: str,
        cost: float,
        business_use_percent: float,
        in_service_date: datetime,
        section_179_available: float,
        business_income_limit: Optional[float] = None,
        useful_life: int = 5,
        override_bonus_percent: Optional[int] = None
    ) -> DepreciationCalculation:
        """
        Calculate maximum deduction by stacking methods:
        1. Use Section 179 first (up to limit)
        2. Use Bonus Depreciation on remaining basis
        3. Use MACRS on any remainder
        
        Args:
            asset_name: Asset identifier
            cost: Purchase cost
            business_use_percent: Business use percentage
            in_service_date: Date placed in service
            section_179_available: Available §179 budget
            business_income_limit: Business income limit
            useful_life: MACRS class life
            override_bonus_percent: Optional override for Bonus %
            
        Returns:
            DepreciationCalculation with stacked totals
        """
        policy = self.tax_policy_service.get_policy_for_date(in_service_date)
        
        # Determine effective bonus percent (Override or Policy)
        effective_bonus_percent = policy.bonus_depreciation_percent
        if override_bonus_percent is not None:
            effective_bonus_percent = override_bonus_percent
            
        depreciable_basis = cost * (business_use_percent / 100.0)
        current_basis = depreciable_basis
        
        notes = []
        
        # Check Strict Business Use Rule (<= 50% forces ADS, no Bonus/179)
        if business_use_percent <= 50.0:
             notes.append("Business Use <= 50%: Section 179 and Bonus disallowed. FORCED MACRS ADS.")
             
             # Calculate ADS
             ads_result = self.calculate_macrs_ads(
                 asset_name=asset_name,
                 cost=cost,
                 business_use_percent=business_use_percent,
                 in_service_date=in_service_date,
                 useful_life=useful_life
             )
             ads_result.method_used = "First_Year_Maximized"
             ads_result.notes = notes + ads_result.notes
             return ads_result

        # --- Step 1: Section 179 ---
        # Calculate how much §179 we CAN take
        section_179_claim = 0.0
        if section_179_available > 0:
            # Theoretical max is the full basis
            # Limited by available budget
            section_179_claim = min(current_basis, section_179_available)
            
            # Limited by business income if provided
            if business_income_limit is not None:
                section_179_claim = min(section_179_claim, business_income_limit)
                
            current_basis -= section_179_claim
            if section_179_claim > 0:
                notes.append(f"§179 applied: ${section_179_claim:,.2f}")
        
        # --- Step 2: Bonus Depreciation ---
        # Applied to remaining basis
        bonus_claim = 0.0
        if current_basis > 0 and effective_bonus_percent > 0:
            bonus_claim = current_basis * (effective_bonus_percent / 100.0)
            current_basis -= bonus_claim
            if bonus_claim > 0:
                notes.append(f"Bonus Depreciation ({effective_bonus_percent}%) on remainder: ${bonus_claim:,.2f}")
                
        # --- Step 3: MACRS GDS ---
        # Applied to any remaining basis (if Bonus < 100%)
        macrs_claim = 0.0
        if current_basis > 0:
            first_year_rate = self.tax_policy_service.get_macrs_first_year_rate(useful_life, in_service_date.year)
            macrs_claim = current_basis * first_year_rate
            current_basis -= macrs_claim
            if macrs_claim > 0:
                 notes.append(f"MACRS GDS remainder: ${macrs_claim:,.2f}")

        # --- Aggregate ---
        total_deduction = section_179_claim + bonus_claim + macrs_claim
        
        result = DepreciationCalculation(
            asset_name=asset_name,
            cost=cost,
            business_use_percent=business_use_percent,
            depreciable_basis=depreciable_basis,
            
            # Fill in individual buckets
            section_179_deduction=section_179_claim,
            bonus_depreciation=bonus_claim,
            macrs_first_year=macrs_claim,
            
            total_first_year_deduction=total_deduction,
            remaining_basis=current_basis,
            method_used="First_Year_Maximized",
            in_service_date=in_service_date
        )
        
        result.notes = notes
        return result