from fastapi import APIRouter, HTTPException
from typing import List
from db.loan_db import LoanInformationDbContext
from models.loan_models import LoanInformationDTO, LoanCreateRequest, LoanUpdateRequest
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize DB context
# In a real app, this might be a dependency injection
loan_db = LoanInformationDbContext()

@router.get("/loans", response_model=List[LoanInformationDTO])
async def get_loans(user_id: int):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
            
        loans = await loan_db.get_loans_async(user_id)
        return loans
    except Exception as e:
        logger.error(f"Error fetching loans: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/loans", response_model=LoanInformationDTO)
async def create_loan(loan: LoanCreateRequest):
    try:
        # Map request to DTO
        loan_dto = LoanInformationDTO(
            asset_id=loan.asset_id,
            user_id=loan.user_id,
            lender_name=loan.lender_name,
            loan_name=loan.loan_name,
            loan_type=loan.loan_type,
            loan_amount=loan.loan_amount,
            interest_rate=loan.interest_rate,
            loan_term_years=loan.loan_term_years,
            remaining_balance=loan.remaining_balance,
            monthly_payment=loan.monthly_payment,
            payment_frequency=loan.payment_frequency,
            status=loan.status,
            last_payment_date=loan.last_payment_date,
            last_payment_amount=loan.last_payment_amount,
            next_payment_date=loan.next_payment_date,
            loan_start_date=loan.loan_start_date,
            loan_end_date=loan.loan_end_date
        )

        # Calculate monthly payment if not provided or 0 (Simple amortization calc)
        if (loan_dto.monthly_payment is None or loan_dto.monthly_payment <= 0) and loan_dto.interest_rate > 0 and loan_dto.loan_term_years > 0:
            r = (loan_dto.interest_rate / 100) / 12
            n = loan_dto.loan_term_years * 12
            if r != 0:
                 # P * r * (1+r)^n / ((1+r)^n - 1)
                 loan_dto.monthly_payment = loan_dto.remaining_balance * (r * (1 + r)**n) / ((1 + r)**n - 1)
            else:
                 loan_dto.monthly_payment = loan_dto.remaining_balance / n

        created_loan = await loan_db.create_loan_record_async(loan_dto)
        if not created_loan:
            raise HTTPException(status_code=500, detail="Failed to create loan record")
            
        return created_loan
    except Exception as e:
        logger.error(f"Error creating loan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/loans/{loan_id}", response_model=LoanInformationDTO)
async def update_loan(loan_id: int, loan: LoanUpdateRequest):
    try:
        if loan.loan_id != loan_id:
             raise HTTPException(status_code=400, detail="Loan ID mismatch")

        # Create DTO
        loan_dto = LoanInformationDTO(
            loan_id=loan_id,
            asset_id=loan.asset_id,
            user_id=loan.user_id,
            lender_name=loan.lender_name,
            loan_name=loan.loan_name,
            loan_type=loan.loan_type,
            loan_amount=loan.loan_amount,
            interest_rate=loan.interest_rate,
            loan_term_years=loan.loan_term_years,
            remaining_balance=loan.remaining_balance,
            monthly_payment=loan.monthly_payment,
            payment_frequency=loan.payment_frequency,
            status=loan.status,
            last_payment_date=loan.last_payment_date,
            last_payment_amount=loan.last_payment_amount,
            next_payment_date=loan.next_payment_date,
            loan_start_date=loan.loan_start_date,
            loan_end_date=loan.loan_end_date
        )

        updated_loan = await loan_db.update_loan_record_async(loan_dto)
        if not updated_loan:
            raise HTTPException(status_code=404, detail="Loan not found")
            
        return updated_loan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating loan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/loans/{loan_id}")
async def delete_loan(loan_id: int):
    try:
        success = await loan_db.delete_loan_record_async(loan_id)
        if not success:
            raise HTTPException(status_code=404, detail="Loan not found")
        return {"message": "Loan deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting loan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
