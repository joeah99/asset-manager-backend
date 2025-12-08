from fastapi import APIRouter, HTTPException, status
from models.auth_models import (
    AppUser,
    RegisterDto,
    LoginDto,
    ChangePasswordDTO,
    VerifyResetTokenDTO,
    ColumnPreferencesDto
)
from db.auth_db import AccountDbContext
from managers.account_manager import AccountManager
import argon2

router = APIRouter()

# Initialize dependencies
account_db_context = AccountDbContext()
account_manager = AccountManager()
ph = argon2.PasswordHasher()


@router.post("/Register", status_code=status.HTTP_200_OK)
async def register(register_dto: RegisterDto):
    """
    Register a new user

    Args:
        register_dto: Registration data

    Returns:
        Created user information
    """
    try:
        # Check if email already exists
        if await account_db_context.user_exists(register_dto.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Account with this email already exists"}
            )

        # Check if username already exists
        if await account_db_context.username_exists(register_dto.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Account with this username already exists"}
            )

        # Create user object with hashed password
        user = AppUser(
            full_name=f"{register_dto.first_name} {register_dto.last_name}",
            username=register_dto.username,
            email=register_dto.email,
            password_hash=ph.hash(register_dto.password)
        )

        # Register user
        created_user = await account_db_context.register_user(user)

        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Failed to create user"}
            )

        # Remove password hash from response
        created_user.password_hash = ""

        return created_user

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.post("/Login")
async def login(login_dto: LoginDto):
    """
    Login user

    Args:
        login_dto: Login credentials

    Returns:
        User information if successful
    """
    try:
        # Check if user exists
        if not await account_db_context.user_exists(login_dto.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Username does not exist"}
            )

        # Validate password
        is_password_valid = await account_db_context.is_password_valid(login_dto)

        if not is_password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid Password"}
            )

        # Get user data
        user = await account_db_context.get_user_by_username(login_dto.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "User not found"}
            )

        return user

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.get("/CheckUsernameExists")
async def check_username_exists(username: str):
    """
    Check if username exists

    Args:
        username: Username to check

    Returns:
        Boolean indicating if username exists
    """
    try:
        response = await account_db_context.username_exists(username)
        return response

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.delete("/DeleteUser")
async def delete_user(email: str):
    """
    Delete a user

    Args:
        email: User email (from request body)

    Returns:
        Success message
    """
    try:
        user_exists = await account_db_context.user_exists(email)

        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "User not found"}
            )

        result = await account_db_context.delete_user(email)

        if result:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Error deleting user"}
            )

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.put("/UpdateUser")
async def update_user(user: AppUser):
    """
    Update user information

    Args:
        user: Updated user data

    Returns:
        Success message
    """
    try:
        result = await account_db_context.update_user(user)

        if result:
            return {"message": "User updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Error updating user"}
            )

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.post("/ForgotPassword")
async def forgot_password(email: str):
    """
    Initiate password reset process

    Args:
        email: User email (from request body)

    Returns:
        Success message
    """
    try:
        password_reset_token = await account_manager.generate_password_reset_token(email)

        if password_reset_token is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Error generating password reset token"}
            )
        else:
            return {"message": "Password reset token generated successfully"}

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.post("/EnterResetToken")
async def enter_reset_token(verify_dto: VerifyResetTokenDTO):
    """
    Verify password reset token

    Args:
        verify_dto: Token and email

    Returns:
        Success message if token is valid
    """
    try:
        token_verified = await account_manager.verify_password_reset_token(
            verify_dto.token,
            verify_dto.email
        )

        if not token_verified:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Invalid password reset token"}
            )
        else:
            return {"message": "Password reset token verified successfully"}

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.put("/ChangePassword")
async def change_password(change_dto: ChangePasswordDTO):
    """
    Change user password

    Args:
        change_dto: New password and email

    Returns:
        Success message
    """
    try:
        # Hash password with Argon2
        password_hash = ph.hash(change_dto.password)

        password_changed = await account_manager.change_password(password_hash, change_dto.email)

        if not password_changed:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Error changing password"}
            )
        else:
            return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.post("/SaveColumnPreferences")
async def save_column_preferences(preferences: ColumnPreferencesDto):
    """
    Save user column preferences

    Args:
        preferences: User ID and preferences JSON

    Returns:
        Success message
    """
    try:
        result = await account_db_context.save_user_column_preferences(
            preferences.user_id,
            preferences.preferences
        )

        if result:
            return {"message": "Column preferences saved successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Error saving column preferences"}
            )

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )


@router.get("/GetColumnPreferences/{userId}")
async def get_column_preferences(userId: int):
    """
    Get user column preferences

    Args:
        userId: User ID

    Returns:
        Column preferences JSON
    """
    try:
        preferences = await account_db_context.get_user_column_preferences(userId)

        if preferences is not None:
            return {"preferences": preferences}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "No column preferences found"}
            )

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(ex)}
        )
