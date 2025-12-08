from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List
from models.loan_models import LoanInformationDTO, LoanScheduleDTO


class LoanInformationService:
    """Service for loan calculations (equivalent to C# LoanInformationService)"""

    def calculate_monthly_payment(self, loan_amount: float, interest_rate: float, loan_term_years: int) -> float:
        """
        Calculate monthly payment using standard amortization formula

        Args:
            loan_amount: Principal loan amount
            interest_rate: Annual interest rate (as percentage, e.g., 5.0 for 5%)
            loan_term_years: Loan term in years

        Returns:
            Monthly payment amount
        """
        # Convert annual percentage to monthly decimal rate
        monthly_interest_rate = interest_rate / 1200.0
        total_payments = loan_term_years * 12

        # Handle zero interest edge case
        if monthly_interest_rate == 0:
            return loan_amount / total_payments if total_payments > 0 else 0.0

        # Standard amortization formula: P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        monthly_payment = (
            (loan_amount * monthly_interest_rate) /
            (1 - pow(1 + monthly_interest_rate, -total_payments))
        )

        return monthly_payment

    def generate_loan_schedule(self, loan: LoanInformationDTO) -> List[LoanScheduleDTO]:
        """
        Generate payment schedule for a loan (simplified version from C#)

        NOTE: This is the original C# implementation that just subtracts monthly payment
        from balance. It does NOT properly calculate interest vs principal per payment.
        We'll improve this in the next step.

        Args:
            loan: Loan information with all details

        Returns:
            List of payment schedule entries
        """
        schedule = []
        remaining_balance = loan.loan_amount
        monthly_payment = loan.monthly_payment

        # Parse start and end dates or default to today and loan term
        if loan.loan_start_date:
            try:
                start_date = datetime.strptime(loan.loan_start_date, "%Y-%m-%d")
            except (ValueError, TypeError):
                start_date = datetime.now()
        else:
            start_date = datetime.now()

        if loan.loan_end_date:
            try:
                end_date = datetime.strptime(loan.loan_end_date, "%Y-%m-%d")
            except (ValueError, TypeError):
                end_date = start_date + relativedelta(months=loan.loan_term_years * 12)
        else:
            end_date = start_date + relativedelta(months=loan.loan_term_years * 12)

        # Start from the next month after the loan start date
        current_date = start_date + relativedelta(months=1)

        while remaining_balance > 0 and current_date <= end_date:
            # Ensure the last payment doesn't overpay
            payment = monthly_payment
            if monthly_payment > remaining_balance:
                payment = remaining_balance
                remaining_balance = 0
            else:
                remaining_balance -= monthly_payment

            schedule.append(LoanScheduleDTO(
                loan_payment_date=current_date.strftime("%Y-%m-%d"),
                new_remaining_value=remaining_balance
            ))

            current_date = current_date + relativedelta(months=1)

        return schedule

    def generate_amortization_schedule(self, loan: LoanInformationDTO) -> List[dict]:
        """
        Generate proper amortization schedule with interest and principal breakdown

        This is the IMPROVED version that properly calculates:
        - Interest portion of each payment
        - Principal portion of each payment
        - Remaining balance after each payment

        Args:
            loan: Loan information with all details

        Returns:
            List of payment schedule entries with interest/principal breakdown
        """
        schedule = []
        remaining_balance = loan.loan_amount
        monthly_payment = loan.monthly_payment
        monthly_interest_rate = loan.interest_rate / 1200.0

        # Parse start date
        if loan.loan_start_date:
            try:
                start_date = datetime.strptime(loan.loan_start_date, "%Y-%m-%d")
            except (ValueError, TypeError):
                start_date = datetime.now()
        else:
            start_date = datetime.now()

        # Calculate end date
        if loan.loan_end_date:
            try:
                end_date = datetime.strptime(loan.loan_end_date, "%Y-%m-%d")
            except (ValueError, TypeError):
                end_date = start_date + relativedelta(months=loan.loan_term_years * 12)
        else:
            end_date = start_date + relativedelta(months=loan.loan_term_years * 12)

        # Start from the next month after the loan start date
        current_date = start_date + relativedelta(months=1)
        payment_number = 1

        while remaining_balance > 0.01 and current_date <= end_date:  # 0.01 to handle floating point precision
            # Calculate interest on remaining balance
            interest_payment = remaining_balance * monthly_interest_rate

            # Calculate principal payment
            principal_payment = monthly_payment - interest_payment

            # Handle last payment
            if principal_payment > remaining_balance:
                principal_payment = remaining_balance
                total_payment = principal_payment + interest_payment
            else:
                total_payment = monthly_payment

            # Update remaining balance
            remaining_balance -= principal_payment

            # Ensure balance doesn't go negative due to floating point errors
            if remaining_balance < 0:
                remaining_balance = 0

            schedule.append({
                "payment_number": payment_number,
                "payment_date": current_date.strftime("%Y-%m-%d"),
                "payment_amount": round(total_payment, 2),
                "principal_payment": round(principal_payment, 2),
                "interest_payment": round(interest_payment, 2),
                "remaining_balance": round(remaining_balance, 2)
            })

            current_date = current_date + relativedelta(months=1)
            payment_number += 1

        return schedule

    def calculate_loan_payoff(
        self,
        loan: LoanInformationDTO,
        payoff_date: str,
        prepayment_penalty_rate: float = 0.0
    ) -> dict:
        """
        Calculate loan payoff amount at a specific date (for liquidation scenarios)

        Args:
            loan: Loan information
            payoff_date: Date when loan will be paid off (YYYY-MM-DD)
            prepayment_penalty_rate: Prepayment penalty as percentage of remaining balance

        Returns:
            Dictionary with payoff details
        """
        try:
            target_date = datetime.strptime(payoff_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            target_date = datetime.now()

        # Generate amortization schedule
        schedule = self.generate_amortization_schedule(loan)

        # Find the payment entry closest to the payoff date
        remaining_balance = loan.loan_amount
        interest_paid_to_date = 0.0
        principal_paid_to_date = 0.0

        for payment in schedule:
            payment_date = datetime.strptime(payment["payment_date"], "%Y-%m-%d")

            if payment_date <= target_date:
                interest_paid_to_date += payment["interest_payment"]
                principal_paid_to_date += payment["principal_payment"]
                remaining_balance = payment["remaining_balance"]
            else:
                # Calculate prorated interest for partial month if payoff is mid-month
                days_in_month = 30  # Simplified - could use actual days
                start_of_month = payment_date - relativedelta(months=1)
                days_elapsed = (target_date - start_of_month).days

                if days_elapsed > 0 and days_elapsed < days_in_month:
                    # Prorate the interest
                    prorated_interest = payment["interest_payment"] * (days_elapsed / days_in_month)
                    interest_paid_to_date += prorated_interest

                break

        # Calculate prepayment penalty
        prepayment_penalty = remaining_balance * (prepayment_penalty_rate / 100.0)

        # Total payoff amount
        total_payoff = remaining_balance + prepayment_penalty

        return {
            "payoff_date": payoff_date,
            "remaining_balance": round(remaining_balance, 2),
            "prepayment_penalty": round(prepayment_penalty, 2),
            "total_payoff_amount": round(total_payoff, 2),
            "total_interest_paid": round(interest_paid_to_date, 2),
            "total_principal_paid": round(principal_paid_to_date, 2),
            "original_loan_amount": loan.loan_amount
        }
