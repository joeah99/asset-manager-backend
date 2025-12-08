import hashlib
import secrets
import base64
from db.auth_db import AccountDbContext
from services.email_service import EmailService


class ForgotPasswordService:
    """Service for handling password reset functionality (equivalent to C# ForgotPasswordService)"""

    def __init__(
        self,
        account_db_context: AccountDbContext = None,
        email_service: EmailService = None
    ):
        self.account_db_context = account_db_context or AccountDbContext()
        self.email_service = email_service or EmailService()

    async def generate_password_reset_token(self, email: str) -> bytes:
        """
        Generate password reset token and send email

        Args:
            email: User email address

        Returns:
            Token hash bytes if successful, None otherwise
        """
        # Check if user exists
        user_exists = await self.account_db_context.user_exists(email)

        if not user_exists:
            return None

        # Generate 6-character alphanumeric code
        reset_code = self.generate_alphanumeric_code()

        # Hash the reset code
        reset_code_bytes = reset_code.encode('utf-8')
        token_hash = self.hash_reset_token(reset_code_bytes)

        # Store hash in database
        result = await self.account_db_context.add_forgot_password_token(
            base64.b64encode(token_hash).decode('utf-8'),
            email
        )

        if not result:
            return None

        # Send email with reset code
        email_sent = await self.email_service.send_password_reset_email(email, reset_code)

        if not email_sent:
            return None

        return token_hash

    async def verify_password_reset_token(self, reset_token: str, email: str) -> bool:
        """
        Verify password reset token

        Args:
            reset_token: 6-character reset code entered by user
            email: User email address

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Hash the provided token
            trimmed_reset_token = reset_token.strip().encode('utf-8')
            reset_token_hash = self.hash_reset_token(trimmed_reset_token)

            # Verify against database
            database_token = await self.account_db_context.verify_password_reset_token(
                base64.b64encode(reset_token_hash).decode('utf-8'),
                email
            )

            return database_token is not None

        except Exception as e:
            print(f"Error verifying password reset token: {e}")
            return False

    def hash_reset_token(self, reset_token: bytes) -> bytes:
        """
        Hash reset token using SHA256

        Args:
            reset_token: Token bytes to hash

        Returns:
            SHA256 hash bytes
        """
        try:
            return hashlib.sha256(reset_token).digest()
        except Exception as e:
            print(f"Error hashing reset token: {e}")
            return None

    def generate_alphanumeric_code(self) -> str:
        """
        Generate a 6-character alphanumeric code

        Returns:
            6-character code string
        """
        # Generate 6 random bytes
        random_bytes = secrets.token_bytes(6)

        # Convert to base64 and take first 6 characters
        code = base64.b64encode(random_bytes).decode('utf-8')[:6]

        # Replace special characters to ensure alphanumeric
        code = code.replace('/', 'A').replace('+', 'B')

        return code
