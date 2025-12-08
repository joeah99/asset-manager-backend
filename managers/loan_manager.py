from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models.loan_models import LoanInformationDTO, LoanProjectedPaymentsDTO, LoanScheduleDTO
from db.loan_db import LoanInformationDbContext, LoanProjectedPaymentsDbContext
from services.loan_service import LoanInformationService


class LoanManager:
    """
    Manager for loan operations (equivalent to C# LoanManager)
    Orchestrates database operations and service calls
    """

    def __init__(
        self,
        db_context: LoanInformationDbContext = None,
        payments_db_context: LoanProjectedPaymentsDbContext = None,
        loan_service: LoanInformationService = None
    ):
        self.db_context = db_context or LoanInformationDbContext()
        self.payments_db_context = payments_db_context or LoanProjectedPaymentsDbContext()
        self.loan_service = loan_service or LoanInformationService()

    async def get_loans(self, user_id: int) -> List[LoanInformationDTO]:
        """
        Get all loans for a user with their payment schedules

        Args:
            user_id: ID of the user

        Returns:
            List of loan information with schedules
        """
        # Get all loans for the user
        loan_list = await self.db_context.get_loans_async(user_id)

        # Get all projected payments for the user
        loan_projected_payments_list = await self.payments_db_context.get_loan_projected_payments_by_user_id_async(user_id)

        # Group payments by loan_id
        payments_by_loan = {}
        for payment in loan_projected_payments_list:
            if payment.loan_id not in payments_by_loan:
                payments_by_loan[payment.loan_id] = []

            payments_by_loan[payment.loan_id].append(
                LoanScheduleDTO(
                    loan_payment_date=payment.loan_payment_date,
                    new_remaining_value=payment.new_remaining_value
                )
            )

        # Build result with updated remaining balances
        result = []
        for loan in loan_list:
            # Get current month's remaining balance from projected payments
            if loan.loan_id in payments_by_loan:
                current_month_payments = [
                    p for p in payments_by_loan[loan.loan_id]
                    if self._is_current_month(p.loan_payment_date)
                ]

                if current_month_payments:
                    # Get the latest payment for current month
                    latest_payment = max(
                        current_month_payments,
                        key=lambda p: datetime.strptime(p.loan_payment_date, "%Y-%m-%d")
                    )
                    loan.remaining_balance = latest_payment.new_remaining_value

                # Attach the loan schedule
                loan.loan_schedule = payments_by_loan[loan.loan_id]
            else:
                loan.loan_schedule = []

            result.append(loan)

        return result

    async def create_loan(self, loan: LoanInformationDTO) -> LoanInformationDTO:
        """
        Create a new loan with payment schedule

        Args:
            loan: Loan information

        Returns:
            Created loan with schedule
        """
        # Calculate monthly payment
        loan.monthly_payment = self.loan_service.calculate_monthly_payment(
            loan.loan_amount,
            loan.interest_rate,
            loan.loan_term_years
        )

        # Set default dates if not provided
        now = datetime.now()

        if not loan.next_payment_date:
            loan.next_payment_date = (now + relativedelta(months=1)).strftime("%Y-%m-%d")

        if not loan.loan_start_date:
            loan.loan_start_date = now.strftime("%Y-%m-%d")

        if not loan.loan_end_date:
            loan.loan_end_date = (now + relativedelta(years=loan.loan_term_years)).strftime("%Y-%m-%d")

        # Create the loan record in database
        new_loan = await self.db_context.create_loan_record_async(loan)

        # Generate payment schedule
        loan_schedule = self.loan_service.generate_loan_schedule(new_loan)

        # Save projected payments to database
        for schedule in loan_schedule:
            payment = LoanProjectedPaymentsDTO(
                loan_projected_payment_id=0,
                loan_id=new_loan.loan_id,
                loan_payment_date=schedule.loan_payment_date,
                new_remaining_value=schedule.new_remaining_value,
                created_at=datetime.utcnow()
            )
            await self.payments_db_context.create_loan_projected_payments_async(payment)

        # Attach schedule to loan
        new_loan.loan_schedule = loan_schedule
        new_loan.loan_creation = datetime.utcnow()
        new_loan.loan_update = datetime.utcnow()

        return new_loan

    async def update_loan(self, loan: LoanInformationDTO) -> LoanInformationDTO:
        """
        Update an existing loan and regenerate payment schedule

        Args:
            loan: Updated loan information

        Returns:
            Updated loan with new schedule
        """
        # Recalculate monthly payment
        loan.monthly_payment = self.loan_service.calculate_monthly_payment(
            loan.loan_amount,
            loan.interest_rate,
            loan.loan_term_years
        )

        # Update the loan record
        updated_loan = await self.db_context.update_loan_record_async(loan)

        if not updated_loan:
            raise Exception("Failed to update loan record")

        # Delete existing projected payments
        deleted = await self.payments_db_context.delete_loan_projected_payments_async(updated_loan.loan_id)

        if not deleted:
            raise Exception("Failed to delete existing loan projected payments")

        # Generate new payment schedule
        loan_schedule = self.loan_service.generate_loan_schedule(updated_loan)

        # Save new projected payments
        for schedule in loan_schedule:
            payment = LoanProjectedPaymentsDTO(
                loan_projected_payment_id=0,
                loan_id=updated_loan.loan_id,
                loan_payment_date=schedule.loan_payment_date,
                new_remaining_value=schedule.new_remaining_value,
                created_at=datetime.utcnow()
            )
            await self.payments_db_context.create_loan_projected_payments_async(payment)

        # Attach schedule to loan
        updated_loan.loan_schedule = loan_schedule
        updated_loan.loan_update = datetime.utcnow()

        return updated_loan

    async def delete_loan(self, loan_id: int) -> bool:
        """
        Delete a loan (projected payments will be cascade deleted)

        Args:
            loan_id: ID of the loan to delete

        Returns:
            True if successful, False otherwise
        """
        result = await self.db_context.delete_loan_record_async(loan_id)
        return result

    def _is_current_month(self, date_string: str) -> bool:
        """Helper to check if a date string is in the current month"""
        try:
            date = datetime.strptime(date_string, "%Y-%m-%d")
            now = datetime.now()
            return date.year == now.year and date.month == now.month
        except (ValueError, TypeError):
            return False
