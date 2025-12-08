from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models.asset_models import AssetDepreciationDTO
import math


class AssetDepreciationService:
    """
    Service for calculating asset depreciation schedules
    (equivalent to C# AssetDepreciationService)

    Supports:
    - Straight-line depreciation
    - Declining balance depreciation
    - Double declining balance depreciation
    - Units of production depreciation
    - Modified Accelerated Cost Recovery System (MACRS)
    """

    def straight_line_depreciation(
        self,
        initial_cost: float,
        salvage_value: float,
        useful_life: int
    ) -> List[AssetDepreciationDTO]:
        """
        Calculate straight-line depreciation schedule

        Formula: Annual Depreciation = (Initial Cost - Salvage Value) / Useful Life
        Monthly Depreciation = Annual Depreciation / 12

        Args:
            initial_cost: Initial cost of the asset
            salvage_value: Expected salvage value at end of useful life
            useful_life: Useful life in years

        Returns:
            List of monthly depreciation entries
        """
        end_of_month_values = []
        annual_depreciation = (initial_cost - salvage_value) / useful_life
        monthly_depreciation = annual_depreciation / 12
        book_value = initial_cost

        # Start from 1 year ago
        current_date = datetime.now().replace(day=1) - relativedelta(years=1)

        for month in range(1, useful_life * 12 + 1):
            book_value -= monthly_depreciation
            if book_value < salvage_value:
                book_value = salvage_value

            end_of_month_values.append(AssetDepreciationDTO(
                depreciation_date=current_date.strftime("%Y-%m-%d"),
                new_book_value=book_value
            ))
            current_date += relativedelta(months=1)

        return end_of_month_values

    def declining_balance_depreciation(
        self,
        initial_cost: float,
        salvage_value: float,
        useful_life: int,
        rate: float
    ) -> List[AssetDepreciationDTO]:
        """
        Calculate declining balance depreciation schedule

        Formula: Monthly Depreciation = Book Value * (Rate / 12)

        Args:
            initial_cost: Initial cost of the asset
            salvage_value: Expected salvage value
            useful_life: Useful life in years
            rate: Depreciation rate (e.g., 0.2 for 20%)

        Returns:
            List of monthly depreciation entries
        """
        book_value = initial_cost
        end_of_month_values = []

        # Start from 1 year ago
        current_date = datetime.now().replace(day=1) - relativedelta(years=1)

        for month in range(1, useful_life * 12 + 1):
            depreciation = book_value * rate / 12
            book_value -= depreciation
            if book_value < salvage_value:
                book_value = salvage_value

            end_of_month_values.append(AssetDepreciationDTO(
                depreciation_date=current_date.strftime("%Y-%m-%d"),
                new_book_value=book_value
            ))
            current_date += relativedelta(months=1)

        return end_of_month_values

    def double_declining_balance_depreciation(
        self,
        initial_cost: float,
        salvage_value: float,
        useful_life: int
    ) -> List[AssetDepreciationDTO]:
        """
        Calculate double declining balance depreciation schedule

        This is a shortcut for declining balance with rate = 2.0 / useful_life

        Args:
            initial_cost: Initial cost of the asset
            salvage_value: Expected salvage value
            useful_life: Useful life in years

        Returns:
            List of monthly depreciation entries
        """
        return self.declining_balance_depreciation(
            initial_cost,
            salvage_value,
            useful_life,
            2.0 / useful_life
        )

    def units_of_production_depreciation(
        self,
        initial_cost: float,
        salvage_value: float,
        total_units: int,
        units_produced_per_year: int
    ) -> List[AssetDepreciationDTO]:
        """
        Calculate units of production depreciation schedule

        Formula: Depreciation per Unit = (Initial Cost - Salvage Value) / Total Units
        Monthly Depreciation = Depreciation per Unit * Units Produced This Month

        Args:
            initial_cost: Initial cost of the asset
            salvage_value: Expected salvage value
            total_units: Total expected units of production
            units_produced_per_year: Expected units produced per year

        Returns:
            List of monthly depreciation entries
        """
        depreciation_per_unit = (initial_cost - salvage_value) / total_units
        end_of_month_values = []
        book_value = initial_cost
        total_months = math.ceil(total_units / units_produced_per_year * 12)

        # Start from 1 year ago
        current_date = datetime.now().replace(day=1) - relativedelta(years=1)

        for month in range(1, total_months + 1):
            units_produced_this_month = min(
                units_produced_per_year // 12,
                total_units - (month - 1) * (units_produced_per_year // 12)
            )
            book_value -= depreciation_per_unit * units_produced_this_month
            if book_value < salvage_value:
                book_value = salvage_value

            end_of_month_values.append(AssetDepreciationDTO(
                depreciation_date=current_date.strftime("%Y-%m-%d"),
                new_book_value=book_value
            ))
            current_date += relativedelta(months=1)

        return end_of_month_values

    def modified_accelerated_cost_recovery_system(
        self,
        initial_cost: float,
        useful_life: int
    ) -> List[AssetDepreciationDTO]:
        """
        Calculate MACRS depreciation schedule

        Uses IRS MACRS rates for 5-year property (common for equipment)

        Args:
            initial_cost: Initial cost of the asset
            useful_life: Useful life in years (not used in MACRS but kept for compatibility)

        Returns:
            List of monthly depreciation entries
        """
        macrs_rates = [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]
        end_of_month_values = []
        book_value = initial_cost

        # Start from 1 year ago
        current_date = datetime.now().replace(day=1) - relativedelta(years=1)

        for year in range(len(macrs_rates)):
            annual_depreciation = initial_cost * macrs_rates[year]
            monthly_depreciation = annual_depreciation / 12

            for month in range(1, 13):
                book_value -= monthly_depreciation
                if book_value < 0:
                    book_value = 0  # Ensure book value doesn't go below zero

                end_of_month_values.append(AssetDepreciationDTO(
                    depreciation_date=current_date.strftime("%Y-%m-%d"),
                    new_book_value=book_value
                ))
                current_date += relativedelta(months=1)

        return end_of_month_values
