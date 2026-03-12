from datetime import datetime
from typing import List, Dict, Optional
from services.depreciation_calculation_service import DepreciationCalculationService, DepreciationCalculation
from services.tax_policy_service import TaxPolicyService

class DepreciationScheduleService:
    def __init__(self, depreciation_service: DepreciationCalculationService = None, tax_policy_service: TaxPolicyService = None):
        self.tax_policy_service = tax_policy_service or TaxPolicyService()
        self.depreciation_service = depreciation_service or DepreciationCalculationService(self.tax_policy_service)

    def generate_schedule(
        self,
        cost: float,
        business_use_percent: float,
        method: str,
        in_service_date: datetime,
        useful_life: int = 5
    ) -> List[Dict]:
        """
        Generates a year-by-year depreciation schedule for the asset.
        """
        schedule = []
        depreciable_basis = cost * (business_use_percent / 100.0)
        remaining_basis = depreciable_basis
        start_year = in_service_date.year
        policy = self.tax_policy_service.get_policy_for_date(in_service_date)
        
        # Determine first year deduction
        first_year_bonus = 0.0
        first_year_179 = 0.0
        
        if method == "BONUS" and business_use_percent > 50:
            bonus_percent = policy.bonus_depreciation_percent
            first_year_bonus = depreciable_basis * (bonus_percent / 100.0)
            remaining_basis -= first_year_bonus
            
        elif method == "SECTION_179" and business_use_percent > 50:
            # Assuming full usage for simplicity on individual schedule view unless limited
            section_179_available = policy.section_179_limit
            first_year_179 = min(depreciable_basis, section_179_available)
            remaining_basis -= first_year_179
            
        elif method == "AUTO" and business_use_percent > 50:
            # Optimal method tries to max out
            section_179_available = policy.section_179_limit
            first_year_179 = min(depreciable_basis, section_179_available)
            remaining_basis -= first_year_179
            
            if remaining_basis > 0:
                bonus_percent = policy.bonus_depreciation_percent
                bonus = remaining_basis * (bonus_percent / 100.0)
                first_year_bonus = bonus
                remaining_basis -= first_year_bonus

        # The remaining basis is then depreciated over the useful life using MACRS
        basis_for_macrs = remaining_basis

        if method == "MACRS_ADS" or business_use_percent <= 50:
            # Straight line over useful_life, half-year convention
            # Years: 1 (half), 2..L (full), L+1 (half)
            ads_rate = 1.0 / useful_life
            
            first_yr_depr = basis_for_macrs * (ads_rate * 0.5)
            first_year_total = first_year_bonus + first_year_179 + first_yr_depr
            
            schedule.append({
                "year": start_year,
                "depreciation": first_year_total,
                "remaining_basis": depreciable_basis - first_year_total
            })
            accumulated = first_year_total
            
            for i in range(1, useful_life):
                depr = basis_for_macrs * ads_rate
                accumulated += depr
                schedule.append({
                    "year": start_year + i,
                    "depreciation": depr,
                    "remaining_basis": max(0, depreciable_basis - accumulated)
                })
                
            # Final half-year
            depr = basis_for_macrs * (ads_rate * 0.5)
            accumulated += depr
            schedule.append({
                "year": start_year + useful_life,
                "depreciation": depr,
                "remaining_basis": max(0, depreciable_basis - accumulated)
            })
            
        else:
            # MACRS GDS (or default fallback for BONUS/179/AUTO/GDS)
            macrs_schedule = policy.macrs_5_year_schedule if useful_life == 5 else policy.macrs_7_year_schedule
            
            accumulated = 0.0
            for i, percent in enumerate(macrs_schedule):
                rate = percent / 100.0
                depr = basis_for_macrs * rate
                
                total_depr = depr
                if i == 0:
                    total_depr += first_year_bonus + first_year_179
                    
                accumulated += total_depr
                schedule.append({
                    "year": start_year + i,
                    "depreciation": total_depr,
                    "remaining_basis": max(0, depreciable_basis - accumulated)
                })

        # Ensure no negative basis or tiny rounding errors
        for s in schedule:
            s["depreciation"] = round(s["depreciation"], 2)
            s["remaining_basis"] = round(s["remaining_basis"], 2)

        return schedule
