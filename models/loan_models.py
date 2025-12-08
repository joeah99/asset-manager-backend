from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LoanScheduleDTO(BaseModel):
    """Represents a single payment in the loan schedule"""
    loan_payment_date: str
    new_remaining_value: float


class LoanProjectedPaymentsDTO(BaseModel):
    """Represents projected payment records stored in the database"""
    loan_projected_payment_id: int = 0
    loan_id: int
    loan_payment_date: str
    new_remaining_value: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LoanInformationDTO(BaseModel):
    """Main loan information model"""
    loan_id: int = 0
    asset_id: int
    user_id: int
    lender_name: str
    loan_amount: float
    interest_rate: float
    loan_term_years: int
    remaining_balance: float
    monthly_payment: float = 0.0
    payment_frequency: str
    status: str
    last_payment_date: Optional[str] = None
    last_payment_amount: Optional[float] = None
    next_payment_date: Optional[str] = None
    loan_start_date: Optional[str] = None
    loan_end_date: Optional[str] = None
    loan_schedule: List[LoanScheduleDTO] = Field(default_factory=list)
    loan_creation: datetime = Field(default_factory=datetime.utcnow)
    loan_update: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True  # For SQLAlchemy/ORM compatibility


class LoanCreateRequest(BaseModel):
    """Request model for creating a loan"""
    asset_id: int
    user_id: int
    lender_name: str
    loan_amount: float
    interest_rate: float
    loan_term_years: int
    remaining_balance: float
    payment_frequency: str = "Monthly"
    status: str = "Active"
    last_payment_date: Optional[str] = None
    last_payment_amount: Optional[float] = None
    next_payment_date: Optional[str] = None
    loan_start_date: Optional[str] = None
    loan_end_date: Optional[str] = None


class LoanUpdateRequest(BaseModel):
    """Request model for updating a loan"""
    loan_id: int
    asset_id: int
    user_id: int
    lender_name: str
    loan_amount: float
    interest_rate: float
    loan_term_years: int
    remaining_balance: float
    monthly_payment: float
    payment_frequency: str
    status: str
    last_payment_date: Optional[str] = None
    last_payment_amount: Optional[float] = None
    next_payment_date: Optional[str] = None
    loan_start_date: Optional[str] = None
    loan_end_date: Optional[str] = None
