from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from models.loan_models import (
    LoanInformationDTO,
    LoanCreateRequest,
    LoanUpdateRequest
)
from managers.loan_manager import LoanManager
from services.loan_impact_service import LoanImpactService

router = APIRouter()

# Initialize manager and services
loan_manager = LoanManager()
loan_impact_service = LoanImpactService()


# Request models for impact calculations
class LiquidationImpactRequest(BaseModel):
    asset_sale_price: float
    existing_loan: Optional[LoanInformationDTO] = None
    liquidation_date: str
    transaction_fees: float = 0.0
    prepayment_penalty_rate: float = 0.0


class ReplacementImpactRequest(BaseModel):
    asset_sale_price: float
    liquidation_date: str
    existing_loan: Optional[LoanInformationDTO] = None
    replacement_asset_price: float
    replacement_loan: Optional[LoanInformationDTO] = None
    transaction_fees: float = 0.0
    prepayment_penalty_rate: float = 0.0


@router.post("/CreateLoanRecord", status_code=status.HTTP_201_CREATED)
async def create_loan_record(loan: LoanCreateRequest):
    """
    Create a new loan record

    Args:
        loan: Loan creation request data

    Returns:
        Created loan with message
    """
    try:
        # Convert request to DTO
        loan_dto = LoanInformationDTO(
            loan_id=0,
            asset_id=loan.asset_id,
            user_id=loan.user_id,
            lender_name=loan.lender_name,
            loan_amount=loan.loan_amount,
            interest_rate=loan.interest_rate,
            loan_term_years=loan.loan_term_years,
            remaining_balance=loan.remaining_balance,
            payment_frequency=loan.payment_frequency,
            status=loan.status,
            last_payment_date=loan.last_payment_date,
            last_payment_amount=loan.last_payment_amount,
            next_payment_date=loan.next_payment_date,
            loan_start_date=loan.loan_start_date,
            loan_end_date=loan.loan_end_date
        )

        new_loan = await loan_manager.create_loan(loan_dto)

        if new_loan:
            return {
                "loan": new_loan,
                "message": "Loan created successfully."
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Loan creation failed."
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating loan: {str(e)}"
        )


@router.post("/GetLoans")
async def get_loans(user_id: int):
    """
    Get all loans for a user

    Args:
        user_id: User ID (passed in request body to match C# implementation)

    Returns:
        List of loans with schedules
    """
    try:
        loans = await loan_manager.get_loans(user_id)

        if loans is not None:
            return loans
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No loan data found."
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching loans: {str(e)}"
        )


@router.put("/UpdateLoan")
async def update_loan(loan: LoanUpdateRequest):
    """
    Update an existing loan

    Args:
        loan: Updated loan data

    Returns:
        Updated loan with message
    """
    try:
        # Convert request to DTO
        loan_dto = LoanInformationDTO(
            loan_id=loan.loan_id,
            asset_id=loan.asset_id,
            user_id=loan.user_id,
            lender_name=loan.lender_name,
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

        result = await loan_manager.update_loan(loan_dto)

        if result:
            return {
                "loan": result,
                "message": "Loan updated successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating loan"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating loan: {str(e)}"
        )


@router.delete("/DeleteLoan")
async def delete_loan(loan_id: int):
    """
    Delete a loan

    Args:
        loan_id: ID of loan to delete (passed in request body to match C# implementation)

    Returns:
        Success message
    """
    try:
        result = await loan_manager.delete_loan(loan_id)

        if result:
            return {"message": "Loan deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting loan"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting loan: {str(e)}"
        )


@router.get("/amortization-schedule/{loan_id}")
async def get_amortization_schedule(loan_id: int):
    """
    Get detailed amortization schedule for a loan with interest/principal breakdown

    Args:
        loan_id: ID of the loan

    Returns:
        Detailed payment schedule with interest and principal breakdown
    """
    try:
        from services.loan_service import LoanInformationService
        from db.loan_db import LoanInformationDbContext

        # Get the loan
        db_context = LoanInformationDbContext()
        loans = await db_context.get_loans_async(loan_id)  # This gets by user_id, we need to adjust

        # For now, we'll need a method to get loan by ID
        # This is a placeholder - you'd want to add a get_loan_by_id method to the DbContext
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Amortization schedule endpoint requires get_loan_by_id implementation"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating amortization schedule: {str(e)}"
        )


@router.post("/payoff-calculation")
async def calculate_payoff(loan_id: int, payoff_date: str, prepayment_penalty_rate: float = 0.0):
    """
    Calculate loan payoff amount for a specific date (useful for liquidation scenarios)

    Args:
        loan_id: ID of the loan
        payoff_date: Date when loan will be paid off (YYYY-MM-DD)
        prepayment_penalty_rate: Prepayment penalty as percentage (default 0.0)

    Returns:
        Payoff calculation details
    """
    try:
        # This is a placeholder - needs get_loan_by_id implementation
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Payoff calculation endpoint requires get_loan_by_id implementation"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating payoff: {str(e)}"
        )


@router.post("/impact/liquidation")
async def calculate_liquidation_impact(request: LiquidationImpactRequest):
    """
    Calculate financial impact of liquidating an asset with an outstanding loan

    This endpoint helps determine net proceeds after paying off the loan,
    including any prepayment penalties and transaction fees.

    Args:
        request: Liquidation impact calculation request

    Returns:
        Detailed liquidation impact analysis
    """
    try:
        impact = loan_impact_service.calculate_liquidation_impact(
            asset_sale_price=request.asset_sale_price,
            existing_loan=request.existing_loan,
            liquidation_date=request.liquidation_date,
            transaction_fees=request.transaction_fees,
            prepayment_penalty_rate=request.prepayment_penalty_rate
        )
        return impact

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating liquidation impact: {str(e)}"
        )


@router.post("/impact/replacement")
async def calculate_replacement_scenario(request: ReplacementImpactRequest):
    """
    Calculate complete financial impact of liquidating an asset and purchasing a replacement

    This endpoint provides comprehensive analysis including:
    - Net proceeds from liquidation
    - Cash required for replacement
    - Monthly payment changes
    - Total interest cost comparison
    - Financial recommendation

    Args:
        request: Replacement scenario calculation request

    Returns:
        Complete scenario analysis with recommendation
    """
    try:
        impact = loan_impact_service.calculate_total_scenario_impact(
            asset_sale_price=request.asset_sale_price,
            liquidation_date=request.liquidation_date,
            existing_loan=request.existing_loan,
            replacement_asset_price=request.replacement_asset_price,
            replacement_loan=request.replacement_loan,
            transaction_fees=request.transaction_fees,
            prepayment_penalty_rate=request.prepayment_penalty_rate
        )
        return impact

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating replacement scenario: {str(e)}"
        )
