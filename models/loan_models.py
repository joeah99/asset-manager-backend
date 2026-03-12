from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


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
    linked_type: Optional[str] = None  # 'asset' or 'purchase'
    linked_id: Optional[int] = None    # ID of the linked asset or purchase
    user_id: int
    lender_name: str
    loan_name: str             # [NEW]
    loan_type: str             # [NEW] (Term, Operating, Lease, etc.)
    loan_amount: float
    interest_rate: float
    loan_term_years: int
    remaining_balance: float
    monthly_payment: float = 0.0
    payment_frequency: str
    status: str
    loan_start_date: Optional[date] = None
    loan_end_date: Optional[date] = None
    ltv: Optional[float] = None
    loan_schedule: List[LoanScheduleDTO] = Field(default_factory=list)
    loan_creation: datetime = Field(default_factory=datetime.utcnow)
    loan_update: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class LoanCreateRequest(BaseModel):
    """Request model for creating a loan"""
    linked_type: Optional[str] = None  # 'asset' or 'purchase'
    linked_id: Optional[int] = None    # ID of the linked asset or purchase
    user_id: int
    lender_name: str
    loan_name: str             # [NEW]
    loan_type: str             # [NEW]
    loan_amount: float
    interest_rate: float
    loan_term_years: int
    remaining_balance: float
    monthly_payment: float = 0.0
    payment_frequency: str = "Monthly"
    status: str = "Active"
    loan_start_date: Optional[date] = None
    loan_end_date: Optional[date] = None
    ltv: Optional[float] = None


class LoanUpdateRequest(BaseModel):
    """Request model for updating a loan"""
    loan_id: int
    linked_type: Optional[str] = None  # 'asset' or 'purchase'
    linked_id: Optional[int] = None    # ID of the linked asset or purchase
    user_id: int
    lender_name: str
    loan_name: str             # [NEW]
    loan_type: str             # [NEW]
    loan_amount: float
    interest_rate: float
    loan_term_years: int
    remaining_balance: float
    monthly_payment: float
    payment_frequency: str
    status: str
    loan_start_date: Optional[date] = None
    loan_end_date: Optional[date] = None
    ltv: Optional[float] = None
