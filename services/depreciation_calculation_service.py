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
        # Get policy for in-service year
        policy = self.tax_policy_service.get_policy_for_date(in_service_date)
        bonus_percent = override_bonus_percent if override_bonus_percent is not None else policy.bonus_depreciation_percent
        
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
        policy = self.tax_policy_service.get_policy_for_date(in_service_date)
        depreciable_basis = cost * (business_use_percent / 100.0)
        
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
        useful_life: int = 5
    ) -> DepreciationCalculation:
        """
        Calculate depreciation using the most beneficial method.
        
        Priority order:
        1. §179 (if available and beneficial)
        2. Bonus (if available and beneficial)
        3. MACRS GDS (default)
        
        Args:
            asset_name: Asset identifier
            cost: Purchase cost
            business_use_percent: Business use percentage
            in_service_date: Date placed in service
            section_179_available: Available §179 budget
            business_income_limit: Business income limit
            useful_life: MACRS class life
            
        Returns:
            DepreciationCalculation with optimal method
        """
        policy = self.tax_policy_service.get_policy_for_date(in_service_date)
        depreciable_basis = cost * (business_use_percent / 100.0)
        
        # Calculate all methods
        section_179_calc = self.calculate_section_179(
            asset_name, cost, business_use_percent, in_service_date,
            section_179_available, business_income_limit
        )
        
        bonus_calc = self.calculate_bonus_depreciation(
            asset_name, cost, business_use_percent, in_service_date
        )
        
        macrs_calc = self.calculate_macrs_gds(
            asset_name, cost, business_use_percent, in_service_date, useful_life
        )
        
        # Choose method with highest first-year deduction
        candidates = [section_179_calc, bonus_calc, macrs_calc]
        optimal = max(candidates, key=lambda x: x.total_first_year_deduction)
        
        optimal.notes.append("Selected optimal depreciation method")
        
        return optimal