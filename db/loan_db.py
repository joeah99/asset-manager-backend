import asyncpg
from typing import List, Optional
from datetime import datetime
from models.loan_models import LoanInformationDTO, LoanProjectedPaymentsDTO
import os
from dotenv import load_dotenv

load_dotenv()


class LoanInformationDbContext:
    """Database operations for loan information (equivalent to C# LoanInformationDbContext)"""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

    async def get_loans_async(self, user_id: int) -> List[LoanInformationDTO]:
        """Get all loans for a specific user"""
        loan_list = []

        conn = await asyncpg.connect(self.connection_string)
        try:
            query = """
                SELECT
                    loan_id, linked_type, linked_id, user_id, lender_name, loan_name, loan_type, loan_amount, interest_rate, loan_term_years,
                    remaining_balance, monthly_payment, payment_frequency, loan_status,
                    loan_start_date, loan_end_date, ltv, created_at, updated_at
                FROM "Loans"
                WHERE user_id = $1
            """

            rows = await conn.fetch(query, user_id)

            for row in rows:
                loan = LoanInformationDTO(
                    loan_id=row['loan_id'],
                    linked_type=row['linked_type'],
                    linked_id=row['linked_id'],
                    user_id=row['user_id'],
                    lender_name=row['lender_name'] or '',
                    loan_name=row['loan_name'] or '',
                    loan_type=row['loan_type'] or '',
                    loan_amount=float(row['loan_amount']) if row['loan_amount'] else 0.0,
                    interest_rate=float(row['interest_rate']) if row['interest_rate'] else 0.0,
                    loan_term_years=row['loan_term_years'] or 0,
                    remaining_balance=float(row['remaining_balance']) if row['remaining_balance'] else 0.0,
                    monthly_payment=float(row['monthly_payment']) if row['monthly_payment'] else 0.0,
                    payment_frequency=row['payment_frequency'] or '',
                    status=row['loan_status'] or '',
                    loan_start_date=row['loan_start_date'],
                    loan_end_date=row['loan_end_date'],
                    ltv=float(row['ltv']) if row['ltv'] is not None else None,
                    loan_creation=row['created_at'] or datetime.utcnow(),
                    loan_update=row['updated_at'] or datetime.utcnow()
                )
                loan_list.append(loan)

        finally:
            await conn.close()

        return loan_list

    async def create_loan_record_async(self, loan: LoanInformationDTO) -> Optional[LoanInformationDTO]:
        """Create a new loan record"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = """
                INSERT INTO "Loans"
                    (linked_type, linked_id, user_id, lender_name, loan_name, loan_type, loan_amount, interest_rate, loan_term_years,
                    remaining_balance, monthly_payment, payment_frequency, loan_status,
                    loan_start_date, loan_end_date, ltv, created_at, updated_at)
                VALUES
                    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NOW(), NOW())
                RETURNING loan_id
            """

            loan_id = await conn.fetchval(
                query,
                loan.linked_type,
                loan.linked_id,
                loan.user_id,
                loan.lender_name or '',
                loan.loan_name or '',
                loan.loan_type or '',
                loan.loan_amount,
                loan.interest_rate,
                loan.loan_term_years,
                loan.remaining_balance,
                loan.monthly_payment,
                loan.payment_frequency or '',
                loan.status or '',
                loan.loan_start_date,
                loan.loan_end_date,
                loan.ltv
            )

            loan.loan_id = loan_id
            return loan

        finally:
            await conn.close()

    async def update_loan_record_async(self, loan: LoanInformationDTO) -> Optional[LoanInformationDTO]:
        """Update an existing loan record"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = """
                UPDATE "Loans"
                SET linked_type = $1,
                    linked_id = $2,
                    user_id = $3,
                    lender_name = $4,
                    loan_name = $5,
                    loan_type = $6,
                    loan_amount = $7,
                    interest_rate = $8,
                    loan_term_years = $9,
                    remaining_balance = $10,
                    monthly_payment = $11,
                    payment_frequency = $12,
                    loan_status = $13,
                    loan_start_date = $14,
                    loan_end_date = $15,
                    ltv = $16,
                    updated_at = NOW()
                WHERE loan_id = $17
            """

            result = await conn.execute(
                query,
                loan.linked_type,
                loan.linked_id,
                loan.user_id,
                loan.lender_name or '',
                loan.loan_name or '',
                loan.loan_type or '',
                loan.loan_amount,
                loan.interest_rate,
                loan.loan_term_years,
                loan.remaining_balance,
                loan.monthly_payment,
                loan.payment_frequency or '',
                loan.status or '',
                loan.loan_start_date,
                loan.loan_end_date,
                loan.ltv,
                loan.loan_id
            )

            # Check if any rows were affected
            rows_affected = int(result.split()[-1])
            return loan if rows_affected > 0 else None

        finally:
            await conn.close()

    async def delete_loan_record_async(self, loan_id: int) -> bool:
        """Delete a loan record"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = 'DELETE FROM "Loans" WHERE loan_id = $1'
            result = await conn.execute(query, loan_id)

            # Check if any rows were affected
            rows_affected = int(result.split()[-1])
            return rows_affected > 0

        finally:
            await conn.close()


class LoanProjectedPaymentsDbContext:
    """Database operations for loan projected payments"""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

    async def create_loan_projected_payments_async(self, loan_payment: LoanProjectedPaymentsDTO) -> LoanProjectedPaymentsDTO:
        """Create a new projected payment record"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = """
                INSERT INTO "LoanProjectedPayments"
                    (loan_id, loan_payment_date, new_remaining_value, created_at)
                VALUES
                    ($1, $2, $3, $4)
                RETURNING loan_projected_payment_id
            """

            loan_projected_payment_id = await conn.fetchval(
                query,
                loan_payment.loan_id,
                loan_payment.loan_payment_date,
                loan_payment.new_remaining_value,
                datetime.utcnow()
            )

            loan_payment.loan_projected_payment_id = loan_projected_payment_id
            return loan_payment

        finally:
            await conn.close()

    async def get_loan_projected_payments_async(self, loan_id: int) -> List[LoanProjectedPaymentsDTO]:
        """Get all projected payments for a specific loan"""
        payment_list = []

        conn = await asyncpg.connect(self.connection_string)
        try:
            query = """
                SELECT
                    loan_projected_payment_id, loan_id, loan_payment_date, new_remaining_value, created_at
                FROM "LoanProjectedPayments"
                WHERE loan_id = $1
            """

            rows = await conn.fetch(query, loan_id)

            for row in rows:
                payment = LoanProjectedPaymentsDTO(
                    loan_projected_payment_id=row['loan_projected_payment_id'],
                    loan_id=row['loan_id'],
                    loan_payment_date=row['loan_payment_date'].strftime("%Y-%m-%d") if isinstance(row['loan_payment_date'], datetime) else row['loan_payment_date'],
                    new_remaining_value=float(row['new_remaining_value']),
                    created_at=row['created_at']
                )
                payment_list.append(payment)

        finally:
            await conn.close()

        return payment_list

    async def delete_loan_projected_payments_async(self, loan_id: int) -> bool:
        """Delete all projected payments for a loan"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = 'DELETE FROM "LoanProjectedPayments" WHERE loan_id = $1'
            result = await conn.execute(query, loan_id)

            # Returns True if any rows were deleted (or if there were none to delete)
            return True

        finally:
            await conn.close()

    async def get_loan_projected_payments_by_user_id_async(self, user_id: int) -> List[LoanProjectedPaymentsDTO]:
        """Get all projected payments for all loans belonging to a user"""
        payment_list = []

        conn = await asyncpg.connect(self.connection_string)
        try:
            query = """
                SELECT
                    p.loan_projected_payment_id, p.loan_id, p.loan_payment_date, p.new_remaining_value, p.created_at
                FROM "LoanProjectedPayments" p
                WHERE p.loan_id IN (
                    SELECT l.loan_id FROM "Loans" l WHERE l.user_id = $1
                )
            """

            rows = await conn.fetch(query, user_id)

            for row in rows:
                payment = LoanProjectedPaymentsDTO(
                    loan_projected_payment_id=row['loan_projected_payment_id'],
                    loan_id=row['loan_id'],
                    loan_payment_date=row['loan_payment_date'].strftime("%Y-%m-%d") if isinstance(row['loan_payment_date'], datetime) else row['loan_payment_date'],
                    new_remaining_value=float(row['new_remaining_value']),
                    created_at=row['created_at']
                )
                payment_list.append(payment)

        finally:
            await conn.close()

        return payment_list
