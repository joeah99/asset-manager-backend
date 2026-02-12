from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    company: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    company: Optional[str] = None
    created_at: Optional[datetime] = None

class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str
