"""
Basis & Recapture Calculation Service

Handles §1245 depreciation recapture and §1231 gain calculations
when assets are sold.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class SaleCalculation:
    """Result of asset sale tax calculation"""
    asset_name: str
    
    # Sale details
    sale_price: float
    original_cost: float
    accumulated_depreciation: float
    adjusted_basis: float  # original_cost - accumulated_depreciation
    
    # Gain/loss breakdown
    total_gain: float  # sale_price - adjusted_basis
    section_1245_recapture: float  # Ordinary income (depreciation recapture)
    section_1231_gain: float  # Capital gain (sale price - original cost, if any)
    
    # After-tax proceeds
    gross_proceeds: float
    transaction_fees: float
    net_proceeds_before_tax: float
    tax_on_recapture: float
    tax_on_capital_gain: float
    net_proceeds_after_tax: float
    
    sale_date: Optional[datetime] = None
    notes: list = None
    
    def __post_init__(self):
        if self.notes is None:
            self.notes = []


class BasisRecaptureService:
    """
    Service for calculating tax basis and recapture on asset sales.
    
    Key concepts:
    - Adjusted Basis = Original Cost - Accumulated Depreciation
    - Total Gain = Sale Price - Adjusted Basis
    - §1245 Recapture = Min(Total Gain, Accumulated Depreciation) → Ordinary Income
    - §1231 Gain = Total Gain - §1245 Recapture → Capital Gain
    """
    
    def calculate_sale_tax_impact(
        self,
        asset_name: str,
        original_cost: float,
        accumulated_depreciation: float,
        sale_price: float,
        transaction_fees: float,
        ordinary_tax_rate: float,  # Marginal rate (e.g., 0.24)
        capital_gains_rate: float = 0.15,  # Long-term cap gains (0%, 15%, or 20%)
        sale_date: Optional[datetime] = None
    ) -> SaleCalculation:
        """
        Calculate complete tax impact of selling a depreciated asset.
        
        Args:
            asset_name: Asset identifier
            original_cost: Original purchase price
            accumulated_depreciation: Total depreciation taken
            sale_price: Expected sale price
            transaction_fees: Auction fees, commissions, etc.
            ordinary_tax_rate: Marginal tax rate for ordinary income
            capital_gains_rate: Long-term capital gains rate (typically 15%)
            sale_date: Date of sale
            
        Returns:
            SaleCalculation with complete breakdown
        """
        # Step 1: Calculate adjusted basis
        adjusted_basis = original_cost - accumulated_depreciation
        
        # Step 2: Calculate total gain
        total_gain = sale_price - adjusted_basis
        
        # Step 3: §1245 Recapture (depreciation taken, taxed as ordinary income)
        section_1245_recapture = min(max(0, total_gain), accumulated_depreciation)
        
        # Step 4: §1231 Gain (any gain above original cost, taxed as capital gain)
        section_1231_gain = max(0, total_gain - section_1245_recapture)
        
        # Step 5: Calculate taxes
        tax_on_recapture = section_1245_recapture * ordinary_tax_rate
        tax_on_capital_gain = section_1231_gain * capital_gains_rate
        total_tax = tax_on_recapture + tax_on_capital_gain
        
        # Step 6: Net proceeds
        gross_proceeds = sale_price
        net_proceeds_before_tax = gross_proceeds - transaction_fees
        net_proceeds_after_tax = net_proceeds_before_tax - total_tax
        
        result = SaleCalculation(
            asset_name=asset_name,
            sale_price=sale_price,
            original_cost=original_cost,
            accumulated_depreciation=accumulated_depreciation,
            adjusted_basis=adjusted_basis,
            total_gain=total_gain,
            section_1245_recapture=section_1245_recapture,
            section_1231_gain=section_1231_gain,
            gross_proceeds=gross_proceeds,
            transaction_fees=transaction_fees,
            net_proceeds_before_tax=net_proceeds_before_tax,
            tax_on_recapture=tax_on_recapture,
            tax_on_capital_gain=tax_on_capital_gain,
            net_proceeds_after_tax=net_proceeds_after_tax,
            sale_date=sale_date
        )
        
        # Add explanatory notes
        result.notes.append(f"Adjusted basis: ${adjusted_basis:,.2f} (${original_cost:,.2f} - ${accumulated_depreciation:,.2f})")
        result.notes.append(f"Total gain: ${total_gain:,.2f}")
        
        if section_1245_recapture > 0:
            result.notes.append(
                f"§1245 recapture (ordinary income): ${section_1245_recapture:,.2f} "
                f"taxed at {ordinary_tax_rate*100:.0f}%"
            )
        
        if section_1231_gain > 0:
            result.notes.append(
                f"§1231 gain (capital gain): ${section_1231_gain:,.2f} "
                f"taxed at {capital_gains_rate*100:.0f}%"
            )
        
        if total_gain < 0:
            result.notes.append(f"Loss on sale: ${abs(total_gain):,.2f}")
        
        return result
    
    def calculate_basis_after_depreciation(
        self,
        original_cost: float,
        depreciation_taken: float
    ) -> float:
        """
        Simple utility to calculate adjusted basis.
        
        Args:
            original_cost: Original purchase price
            depreciation_taken: Total depreciation deductions taken
            
        Returns:
            Adjusted basis (cost - depreciation)
        """
        return max(0, original_cost - depreciation_taken)
    
    def calculate_accumulated_depreciation_estimate(
        self,
        original_cost: float,
        purchase_date: datetime,
        useful_life: int = 5,
        method: str = "MACRS_GDS"
    ) -> float:
        """
        Estimate accumulated depreciation for an asset.
        
        This is a simplified estimate. In production, you'd query
        the actual depreciation schedule from the database.
        
        Args:
            original_cost: Original cost
            purchase_date: Date asset was purchased
            useful_life: MACRS class life
            method: Depreciation method used
            
        Returns:
            Estimated accumulated depreciation
        """
        years_elapsed = (datetime.now() - purchase_date).days / 365.25
        
        if method == "MACRS_GDS" and useful_life == 5:
            # Simplified MACRS 5-year: 20%, 32%, 19.2%, 11.52%, 11.52%, 5.76%
            schedule = [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]
            
            full_years = min(int(years_elapsed), len(schedule))
            accumulated = sum(schedule[:full_years]) * original_cost
            
            return accumulated
        
        elif method == "STRAIGHT_LINE":
            # Simple straight-line
            return min(original_cost, (original_cost / useful_life) * years_elapsed)
        
        else:
            # Default to straight-line estimate
            return min(original_cost, (original_cost / useful_life) * years_elapsed)