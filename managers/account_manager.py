from db.auth_db import AccountDbContext
from services.password_reset_service import ForgotPasswordService


class AccountManager:
    """
    Manager for account operations (equivalent to C# AccountManager)
    Orchestrates database operations and password reset service
    """

    def __init__(
        self,
        account_db_context: AccountDbContext = None,
        forgot_password_service: ForgotPasswordService = None
    ):
        self.account_db_context = account_db_context or AccountDbContext()
        self.forgot_password_service = forgot_password_service or ForgotPasswordService()

    async def generate_password_reset_token(self, email: str) -> bytes:
        """
        Generate password reset token and send email

        Args:
            email: User email address

        Returns:
            Token hash if successful, None otherwise
        """
        try:
            return await self.forgot_password_service.generate_password_reset_token(email)
        except Exception as e:
            print(f"Error generating password reset token: {e}")
            return None

    async def change_password(self, password_hash: str, email: str) -> bool:
        """
        Change user password

        Args:
            password_hash: Hashed password
            email: User email address

        Returns:
            True if successful, False otherwise
        """
        try:
            return await self.account_db_context.change_password(password_hash, email)
        except Exception as e:
            print(f"Error changing password: {e}")
            return False

    async def verify_password_reset_token(self, reset_token: str, email: str) -> bool:
        """
        Verify password reset token

        Args:
            reset_token: Reset code entered by user
            email: User email address

        Returns:
            True if token is valid, False otherwise
        """
        try:
            return await self.forgot_password_service.verify_password_reset_token(reset_token, email)
        except Exception as e:
            print(f"Error verifying password reset token: {e}")
            return False
