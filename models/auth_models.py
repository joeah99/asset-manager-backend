from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class AppUser(BaseModel):
    """User model"""
    id: int = 0
    full_name: str
    username: str
    company: Optional[str] = ""
    email: EmailStr
    password_hash: Optional[str] = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RegisterDto(BaseModel):
    """User registration request"""
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=20)


class LoginDto(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class ChangePasswordDTO(BaseModel):
    """Change password request"""
    password: str
    email: EmailStr


class VerifyResetTokenDTO(BaseModel):
    """Verify password reset token request"""
    token: str
    email: EmailStr


class ColumnPreferencesDto(BaseModel):
    """User column preferences"""
    user_id: int = Field(alias="UserId")
    preferences: str = Field(alias="Preferences")

    class Config:
        populate_by_name = True
