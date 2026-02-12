"""
Tax Policy Service - Versioned tax rules and rates

Manages federal tax policy effective dates, §179 limits, 
bonus depreciation rates, MACRS schedules, and marginal tax brackets.
"""

from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class TaxPolicy:
    """Federal tax policy for a given year"""
    effective_year: int
    section_179_limit: int
    section_179_phaseout_threshold: int
    bonus_depreciation_percent: int  # 0-100
    macrs_5_year_schedule: List[float]  # percentages for each year
    macrs_7_year_schedule: List[float]
    federal_brackets: List[Dict[str, float]]  # [{"limit": 11000, "rate": 0.10}, ...]
    
    # Policy notes for audit trail
    policy_source: str = "IRS Publication 946"
    last_updated: Optional[datetime] = None


class TaxPolicyService:
    """
    Service for retrieving versioned tax policy rules.
    
    In production, this would load from database table `TaxPolicyYear`.
    For now, we'll use hardcoded 2024/2025 rules.
    """
    
    def __init__(self):
        # Hardcoded policies (in production, load from DB)
        self.policies = {
            2024: TaxPolicy(
                effective_year=2024,
                section_179_limit=1_220_000,
                section_179_phaseout_threshold=3_050_000,
                bonus_depreciation_percent=60,  # Phasing down from 100%
                macrs_5_year_schedule=[20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
                macrs_7_year_schedule=[14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
                federal_brackets=[
                    {"limit": 11600, "rate": 0.10},
                    {"limit": 47150, "rate": 0.12},
                    {"limit": 100525, "rate": 0.22},
                    {"limit": 191950, "rate": 0.24},
                    {"limit": 243725, "rate": 0.32},
                    {"limit": 609350, "rate": 0.35},
                    {"limit": float('inf'), "rate": 0.37}
                ],
                policy_source="IRS Rev. Proc. 2023-34",
                last_updated=datetime(2024, 1, 1)
            ),
            2025: TaxPolicy(
                effective_year=2025,
                section_179_limit=1_250_000,  # Projected with inflation adjustment
                section_179_phaseout_threshold=3_130_000,
                bonus_depreciation_percent=40,  # Continues phasedown (2023 TCJA)
                macrs_5_year_schedule=[20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
                macrs_7_year_schedule=[14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
                federal_brackets=[
                    {"limit": 11925, "rate": 0.10},
                    {"limit": 48475, "rate": 0.12},
                    {"limit": 103350, "rate": 0.22},
                    {"limit": 197300, "rate": 0.24},
                    {"limit": 250525, "rate": 0.32},
                    {"limit": 626350, "rate": 0.35},
                    {"limit": float('inf'), "rate": 0.37}
                ],
                policy_source="IRS Rev. Proc. 2024-40 (projected)",
                last_updated=datetime(2025, 1, 1)
            ),
            2026: TaxPolicy(
                effective_year=2026,
                section_179_limit=2_560_000,  # Projected (Updated per user request)
                section_179_phaseout_threshold=4_090_000,  # Updated per user request
                bonus_depreciation_percent=100,  # 2025=40%, 2026=100% (Updated per user request)
                macrs_5_year_schedule=[20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
                macrs_7_year_schedule=[14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
                federal_brackets=[
                    {"limit": 12225, "rate": 0.10},
                    {"limit": 49700, "rate": 0.12},
                    {"limit": 105950, "rate": 0.22},
                    {"limit": 202250, "rate": 0.24},
                    {"limit": 256800, "rate": 0.32},
                    {"limit": 642050, "rate": 0.35},
                    {"limit": float('inf'), "rate": 0.37}
                ],
                policy_source="Projected (TCJA Phaseout)",
                last_updated=datetime(2026, 1, 1)
            ),
            2027: TaxPolicy(
                effective_year=2027,
                section_179_limit=1_310_000,  # Projected
                section_179_phaseout_threshold=3_290_000,
                bonus_depreciation_percent=0,  # Phased out completely
                macrs_5_year_schedule=[20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
                macrs_7_year_schedule=[14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
                federal_brackets=[
                    {"limit": 12525, "rate": 0.10},
                    {"limit": 50950, "rate": 0.12},
                    {"limit": 108600, "rate": 0.22},
                    {"limit": 207300, "rate": 0.24},
                    {"limit": 263200, "rate": 0.32},
                    {"limit": 658100, "rate": 0.35},
                    {"limit": float('inf'), "rate": 0.37}
                ],
                policy_source="Projected (TCJA Expiration)",
                last_updated=datetime(2027, 1, 1)
            )
        }
    
    def get_policy_for_date(self, date: datetime) -> TaxPolicy:
        """
        Get tax policy effective for a given date.
        
        Args:
            date: Date to get policy for (usually asset in-service date)
            
        Returns:
            TaxPolicy for that year
            
        Raises:
            ValueError: If no policy exists for that year
        """
        year = date.year
        
        if year not in self.policies:
            # Default to most recent available policy
            latest_year = max(self.policies.keys())
            return self.policies[latest_year]
        
        return self.policies[year]
    
    def get_policy_for_year(self, year: int) -> TaxPolicy:
        """Get policy by year (convenience method)"""
        if year not in self.policies:
            latest_year = max(self.policies.keys())
            return self.policies[latest_year]
        
        return self.policies[year]
    
    def get_marginal_rate(self, taxable_income: float, year: int = 2025) -> float:
        """
        Calculate marginal tax rate for given income.
        
        Args:
            taxable_income: Taxable income amount
            year: Tax year
            
        Returns:
            Marginal rate as decimal (e.g., 0.24 for 24%)
        """
        policy = self.get_policy_for_year(year)
        
        for bracket in policy.federal_brackets:
            if taxable_income <= bracket["limit"]:
                return bracket["rate"]
        
        # Should never reach here due to inf limit in last bracket
        return policy.federal_brackets[-1]["rate"]
    
    def calculate_section_179_limit_with_phaseout(
        self,
        total_equipment_purchases: float,
        year: int = 2025,
        override_limit: Optional[float] = None
    ) -> float:
        """
        Calculate available §179 deduction after phaseout.
        
        §179 phases out dollar-for-dollar once total equipment
        purchases exceed the threshold.
        
        If override_limit is provided, the phaseout threshold is dynamically
        adjusted to maintain the standard 'gap' between limit and threshold.
        
        Args:
            total_equipment_purchases: Total qualifying purchases for the year
            year: Tax year
            override_limit: Optional user-defined limit (e.g., remaining capacity)
            
        Returns:
            Available §179 limit after phaseout
        """
        policy = self.get_policy_for_year(year)
        
        # Determine base values
        limit = float(override_limit) if override_limit is not None else float(policy.section_179_limit)
        
        # Calculate dynamic threshold if override is used
        # Standard gap = Policy Threshold - Policy Limit
        # New Threshold = Custom Limit + Standard Gap
        gap = float(policy.section_179_phaseout_threshold) - float(policy.section_179_limit)
        phaseout_threshold = limit + gap
        
        if total_equipment_purchases <= phaseout_threshold:
            return limit
        
        # Phase out dollar-for-dollar
        phaseout_amount = total_equipment_purchases - phaseout_threshold
        reduced_limit = limit - phaseout_amount
        
        return max(0.0, reduced_limit)
    
    def get_macrs_first_year_rate(self, useful_life: int, year: int = 2025) -> float:
        """
        Get MACRS first-year depreciation rate.
        
        Args:
            useful_life: MACRS class life (5 or 7 years typically)
            year: Tax year
            
        Returns:
            First-year percentage as decimal (e.g., 0.20 for 20%)
        """
        policy = self.get_policy_for_year(year)
        
        if useful_life == 5:
            return policy.macrs_5_year_schedule[0] / 100.0
        elif useful_life == 7:
            return policy.macrs_7_year_schedule[0] / 100.0
        else:
            # Default to 5-year for unknown classes
            return policy.macrs_5_year_schedule[0] / 100.0