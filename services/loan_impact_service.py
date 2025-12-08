from typing import Optional, Dict
from models.loan_models import LoanInformationDTO
from services.loan_service import LoanInformationService


class LoanImpactService:
    """
    Service for calculating loan impact on asset liquidation and replacement decisions
    """

    def __init__(self, loan_service: LoanInformationService = None):
        self.loan_service = loan_service or LoanInformationService()

    def calculate_liquidation_impact(
        self,
        asset_sale_price: float,
        existing_loan: Optional[LoanInformationDTO],
        liquidation_date: str,
        transaction_fees: float = 0.0,
        prepayment_penalty_rate: float = 0.0
    ) -> Dict:
        """
        Calculate the financial impact of liquidating an asset with an outstanding loan

        Args:
            asset_sale_price: Expected sale price of the asset
            existing_loan: Current loan on the asset (None if no loan)
            liquidation_date: Date when asset will be sold (YYYY-MM-DD)
            transaction_fees: Fees associated with the sale (commissions, legal, etc.)
            prepayment_penalty_rate: Prepayment penalty as percentage of remaining balance

        Returns:
            Dictionary with liquidation impact details
        """
        if existing_loan:
            # Calculate loan payoff amount
            payoff_info = self.loan_service.calculate_loan_payoff(
                existing_loan,
                liquidation_date,
                prepayment_penalty_rate
            )

            loan_payoff = payoff_info["total_payoff_amount"]
            remaining_balance = payoff_info["remaining_balance"]
            prepayment_penalty = payoff_info["prepayment_penalty"]
            total_interest_paid = payoff_info["total_interest_paid"]

            # Calculate interest savings (interest that won't be paid)
            full_schedule = self.loan_service.generate_amortization_schedule(existing_loan)
            total_interest_if_kept = sum(payment["interest_payment"] for payment in full_schedule)
            interest_savings = total_interest_if_kept - total_interest_paid

        else:
            loan_payoff = 0.0
            remaining_balance = 0.0
            prepayment_penalty = 0.0
            total_interest_paid = 0.0
            interest_savings = 0.0

        # Calculate net proceeds
        gross_proceeds = asset_sale_price
        total_costs = transaction_fees + loan_payoff
        net_proceeds = gross_proceeds - total_costs

        return {
            "asset_sale_price": round(asset_sale_price, 2),
            "transaction_fees": round(transaction_fees, 2),
            "loan_payoff": {
                "has_loan": existing_loan is not None,
                "remaining_balance": round(remaining_balance, 2),
                "prepayment_penalty": round(prepayment_penalty, 2),
                "total_payoff_amount": round(loan_payoff, 2),
                "interest_paid_to_date": round(total_interest_paid, 2),
                "interest_savings": round(interest_savings, 2)
            },
            "gross_proceeds": round(gross_proceeds, 2),
            "total_costs": round(total_costs, 2),
            "net_proceeds": round(net_proceeds, 2),
            "liquidation_date": liquidation_date
        }

    def calculate_replacement_impact(
        self,
        liquidation_impact: Dict,
        replacement_asset_price: float,
        replacement_loan: Optional[LoanInformationDTO],
        existing_loan: Optional[LoanInformationDTO]
    ) -> Dict:
        """
        Calculate the financial impact of replacing a liquidated asset with a new one

        Args:
            liquidation_impact: Result from calculate_liquidation_impact
            replacement_asset_price: Price of the replacement asset
            replacement_loan: Loan terms for the replacement asset (None if paying cash)
            existing_loan: Loan on the liquidated asset (for comparison)

        Returns:
            Dictionary with replacement impact details
        """
        net_proceeds = liquidation_impact["net_proceeds"]

        # Calculate down payment needed
        if replacement_loan:
            down_payment = replacement_asset_price - replacement_loan.loan_amount
        else:
            down_payment = replacement_asset_price

        # Calculate cash required (negative means cash left over)
        cash_required = down_payment - net_proceeds

        # Calculate monthly payment changes
        if existing_loan and replacement_loan:
            old_monthly_payment = existing_loan.monthly_payment
            new_monthly_payment = replacement_loan.monthly_payment
            monthly_payment_change = new_monthly_payment - old_monthly_payment
        elif existing_loan and not replacement_loan:
            old_monthly_payment = existing_loan.monthly_payment
            new_monthly_payment = 0.0
            monthly_payment_change = -old_monthly_payment
        elif not existing_loan and replacement_loan:
            old_monthly_payment = 0.0
            new_monthly_payment = replacement_loan.monthly_payment
            monthly_payment_change = new_monthly_payment
        else:
            old_monthly_payment = 0.0
            new_monthly_payment = 0.0
            monthly_payment_change = 0.0

        # Calculate total interest over life of loans
        if replacement_loan:
            replacement_schedule = self.loan_service.generate_amortization_schedule(replacement_loan)
            total_interest_new_loan = sum(payment["interest_payment"] for payment in replacement_schedule)
        else:
            total_interest_new_loan = 0.0

        if existing_loan:
            existing_schedule = self.loan_service.generate_amortization_schedule(existing_loan)
            total_interest_old_loan = sum(payment["interest_payment"] for payment in existing_schedule)
        else:
            total_interest_old_loan = 0.0

        interest_cost_change = total_interest_new_loan - total_interest_old_loan

        return {
            "replacement_asset_price": round(replacement_asset_price, 2),
            "net_proceeds_from_liquidation": round(net_proceeds, 2),
            "down_payment_required": round(down_payment, 2),
            "cash_required": round(cash_required, 2),
            "cash_surplus": round(-cash_required, 2) if cash_required < 0 else 0.0,
            "monthly_payment_comparison": {
                "old_monthly_payment": round(old_monthly_payment, 2),
                "new_monthly_payment": round(new_monthly_payment, 2),
                "monthly_change": round(monthly_payment_change, 2),
                "monthly_change_percent": round((monthly_payment_change / old_monthly_payment * 100), 2) if old_monthly_payment > 0 else 0.0
            },
            "interest_cost_comparison": {
                "total_interest_old_loan": round(total_interest_old_loan, 2),
                "total_interest_new_loan": round(total_interest_new_loan, 2),
                "interest_cost_change": round(interest_cost_change, 2),
                "interest_saved": round(-interest_cost_change, 2) if interest_cost_change < 0 else 0.0
            },
            "loan_terms_comparison": {
                "has_old_loan": existing_loan is not None,
                "has_new_loan": replacement_loan is not None,
                "old_loan_term_months": existing_loan.loan_term_years * 12 if existing_loan else 0,
                "new_loan_term_months": replacement_loan.loan_term_years * 12 if replacement_loan else 0,
                "old_interest_rate": existing_loan.interest_rate if existing_loan else 0.0,
                "new_interest_rate": replacement_loan.interest_rate if replacement_loan else 0.0
            }
        }

    def calculate_total_scenario_impact(
        self,
        asset_sale_price: float,
        liquidation_date: str,
        existing_loan: Optional[LoanInformationDTO],
        replacement_asset_price: float,
        replacement_loan: Optional[LoanInformationDTO],
        transaction_fees: float = 0.0,
        prepayment_penalty_rate: float = 0.0
    ) -> Dict:
        """
        Calculate the complete financial impact of a liquidation and replacement scenario

        Args:
            asset_sale_price: Sale price of the liquidated asset
            liquidation_date: Date when asset will be sold (YYYY-MM-DD)
            existing_loan: Current loan on asset being sold
            replacement_asset_price: Price of replacement asset
            replacement_loan: Loan for replacement asset
            transaction_fees: Transaction fees for the sale
            prepayment_penalty_rate: Prepayment penalty rate

        Returns:
            Complete scenario analysis
        """
        # Calculate liquidation impact
        liquidation = self.calculate_liquidation_impact(
            asset_sale_price,
            existing_loan,
            liquidation_date,
            transaction_fees,
            prepayment_penalty_rate
        )

        # Calculate replacement impact
        replacement = self.calculate_replacement_impact(
            liquidation,
            replacement_asset_price,
            replacement_loan,
            existing_loan
        )

        # Calculate overall financial summary
        net_cash_impact = replacement["cash_required"]
        monthly_obligation_change = replacement["monthly_payment_comparison"]["monthly_change"]
        annual_obligation_change = monthly_obligation_change * 12

        # Determine if this is a good financial decision
        recommendation = self._generate_recommendation(liquidation, replacement)

        return {
            "scenario_summary": {
                "liquidation_date": liquidation_date,
                "net_cash_impact": round(net_cash_impact, 2),
                "net_cash_surplus": round(-net_cash_impact, 2) if net_cash_impact < 0 else 0.0,
                "monthly_obligation_change": round(monthly_obligation_change, 2),
                "annual_obligation_change": round(annual_obligation_change, 2),
                "interest_savings_from_payoff": round(liquidation["loan_payoff"]["interest_savings"], 2),
                "total_interest_cost_change": round(replacement["interest_cost_comparison"]["interest_cost_change"], 2)
            },
            "liquidation_details": liquidation,
            "replacement_details": replacement,
            "recommendation": recommendation
        }

    def _generate_recommendation(self, liquidation: Dict, replacement: Dict) -> Dict:
        """Generate a recommendation based on the financial analysis"""
        factors = []
        positive_score = 0
        negative_score = 0

        # Check net proceeds
        if liquidation["net_proceeds"] > 0:
            factors.append("Liquidation generates positive net proceeds")
            positive_score += 1
        else:
            factors.append("Liquidation results in net loss")
            negative_score += 1

        # Check monthly payment change
        monthly_change = replacement["monthly_payment_comparison"]["monthly_change"]
        if monthly_change < 0:
            factors.append(f"Monthly payment decreases by ${abs(monthly_change):.2f}")
            positive_score += 1
        elif monthly_change > 0:
            factors.append(f"Monthly payment increases by ${monthly_change:.2f}")
            negative_score += 1

        # Check interest cost change
        interest_change = replacement["interest_cost_comparison"]["interest_cost_change"]
        if interest_change < 0:
            factors.append(f"Total interest savings of ${abs(interest_change):.2f}")
            positive_score += 2  # Weight this more heavily
        elif interest_change > 0:
            factors.append(f"Increased interest costs of ${interest_change:.2f}")
            negative_score += 2

        # Check cash requirement
        if replacement["cash_required"] <= 0:
            factors.append("No additional cash required (surplus available)")
            positive_score += 1
        else:
            factors.append(f"Additional cash required: ${replacement['cash_required']:.2f}")
            negative_score += 1

        # Determine overall recommendation
        if positive_score > negative_score * 1.5:
            recommendation_text = "Favorable - This scenario shows strong financial benefits"
        elif positive_score > negative_score:
            recommendation_text = "Moderately Favorable - This scenario has some financial benefits"
        elif positive_score == negative_score:
            recommendation_text = "Neutral - This scenario has balanced pros and cons"
        else:
            recommendation_text = "Unfavorable - This scenario may have negative financial impacts"

        return {
            "recommendation": recommendation_text,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "key_factors": factors
        }
