"""
Tax Policy Service - Versioned tax rules and rates

Manages federal tax policy effective dates, §179 limits, 
bonus depreciation rates, MACRS schedules, and marginal tax brackets.

Loads from the TaxPolicyYear database table at startup.
Falls back to hardcoded defaults if DB is unavailable.
"""

from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


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


# ============================================================
# HARDCODED FALLBACK POLICIES
# Used only when the database is unavailable or empty.
# Once the DB is seeded, these are a safety net only.
# ============================================================
_FALLBACK_POLICIES = {
    2024: TaxPolicy(
        effective_year=2024,
        section_179_limit=1_220_000,
        section_179_phaseout_threshold=3_050_000,
        bonus_depreciation_percent=60,
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
        section_179_limit=1_250_000,
        section_179_phaseout_threshold=3_130_000,
        bonus_depreciation_percent=40,
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
        section_179_limit=2_560_000,
        section_179_phaseout_threshold=4_090_000,
        bonus_depreciation_percent=100,
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
        section_179_limit=1_310_000,
        section_179_phaseout_threshold=3_290_000,
        bonus_depreciation_percent=0,
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


class TaxPolicyService:
    """
    Service for retrieving versioned tax policy rules.
    
    Loads policies from the TaxPolicyYear database table.
    Falls back to hardcoded defaults if the DB is empty or unavailable.
    """
    
    def __init__(self):
        # Start with fallback policies (synchronous — always available)
        self.policies: Dict[int, TaxPolicy] = dict(_FALLBACK_POLICIES)
        self._loaded_from_db = False
    
    async def load_policies_from_db(self):
        """
        Load policies from the TaxPolicyYear database table.
        Replaces the fallback policies if successful.
        
        Call this at application startup (e.g., FastAPI lifespan event).
        """
        try:
            from db.tax_policy_db import TaxPolicyDbContext
            
            db = TaxPolicyDbContext()
            rows = await db.get_all_policies_async()
            
            if not rows:
                logger.warning("TaxPolicyYear table is empty — using hardcoded fallback policies.")
                return
            
            # Convert DB rows to TaxPolicy objects and replace in-memory cache
            db_policies = {}
            for row in rows:
                # Convert the large integer bracket limits back to float('inf') for the last bracket
                brackets = []
                for b in row.federal_brackets:
                    limit = b.get("limit", 0)
                    # Treat very large numbers (999999999+) as infinity
                    if limit >= 999_999_999:
                        limit = float('inf')
                    brackets.append({"limit": limit, "rate": b["rate"]})
                
                policy = TaxPolicy(
                    effective_year=row.tax_year,
                    section_179_limit=row.section_179_limit,
                    section_179_phaseout_threshold=row.section_179_phaseout_threshold,
                    bonus_depreciation_percent=row.bonus_depreciation_percent,
                    macrs_5_year_schedule=row.macrs_5yr_schedule,
                    macrs_7_year_schedule=row.macrs_7yr_schedule,
                    federal_brackets=brackets,
                    policy_source=row.policy_source,
                    last_updated=row.last_updated
                )
                db_policies[row.tax_year] = policy
            
            self.policies = db_policies
            self._loaded_from_db = True
            logger.info(f"Loaded {len(db_policies)} tax policies from database: years {sorted(db_policies.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to load tax policies from DB — using fallback: {e}")
            # Keep using fallback policies
    
    async def reload_policies(self):
        """Force a reload from the database (e.g., after an admin edit)."""
        await self.load_policies_from_db()
    
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
    
    def get_available_years(self) -> List[int]:
        """Get all available tax policy years (sorted)."""
        return sorted(self.policies.keys())