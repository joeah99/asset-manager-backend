from fastapi import APIRouter, HTTPException, status
from models.auth_models import LoginRequest, SignupRequest, UserResponse
from db.auth_db import AuthDbContext
import logging

router = APIRouter()
auth_db = AuthDbContext()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=UserResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user
    """
    print(f"DEBUG: Login request received for {request.email}")
    try:
        user = await auth_db.login_user_async(request.email, request.password)
        print(f"DEBUG: Login result: {user}")
        if not user:
            print("DEBUG: Login failed - user not found or invalid password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Login exception: {e}")
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/signup", response_model=UserResponse)
async def signup(request: SignupRequest):
    """
    Register a new user
    """
    print(f"DEBUG: Signup request received for {request.email}")
    try:
        user = await auth_db.create_user_async(request)
        print(f"DEBUG: Signup result: {user}")
        if not user:
            print("DEBUG: Signup failed - user already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Signup exception: {e}")
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
