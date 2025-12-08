from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Service for sending emails using SendGrid (equivalent to C# EmailService)"""

    def __init__(self, sendgrid_api_key: str = None):
        self.sendgrid_api_key = sendgrid_api_key or os.getenv("SENDGRID_API_KEY")

    async def send_password_reset_email(self, email: str, reset_code: str) -> bool:
        """
        Send password reset email with reset code

        Args:
            email: Recipient email address
            reset_code: 6-character reset code

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            message = Mail(
                from_email=('no-reply@dpaauctions.com', 'DPA Auctions'),
                to_emails=email,
                subject='Asset Manager Password Reset Request',
                plain_text_content=f'You requested a password reset. Use the following code to reset your password: {reset_code}',
                html_content=f'''
                    <p>You requested a password reset.</p>
                    <p>Use the following code to reset your password:</p>
                    <div style='text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0;'>
                        {reset_code}
                    </div>
                '''
            )

            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)

            # Check if email was accepted
            return response.status_code == 202  # SendGrid returns 202 Accepted

        except Exception as e:
            print(f"Error sending email: {e}")
            return False
