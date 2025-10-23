using SendGrid;
using SendGrid.Helpers.Mail;
using System;
using System.Threading.Tasks;
using API.Services;

namespace API.Services
{
    public class EmailService
    {
        private readonly string _sendGridApiKey;

        public EmailService(string sendGridApiKey)
        {
            _sendGridApiKey = sendGridApiKey;
        }

        public async Task<bool> SendPasswordResetEmail(string email, string resetCode)
        {
            try
            {
                var client = new SendGridClient(_sendGridApiKey);
                var from = new EmailAddress("no-reply@dpaauctions.com", "DPA Auctions");
                var subject = "Asset Manager Password Reset Request";
                var to = new EmailAddress(email);
                var plainTextContent = $"You requested a password reset. Use the following code to reset your password: {resetCode}";
                var htmlContent = $@"
                    <p>You requested a password reset.</p>
                    <p>Use the following code to reset your password:</p>
                    <div style='text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0;'>
                        {resetCode}
                    </div>";
                    
                var message = MailHelper.CreateSingleEmail(from, to, subject, plainTextContent, htmlContent);

                var response = await client.SendEmailAsync(message);

                // Check if the email was sent successfully
                return response.StatusCode == System.Net.HttpStatusCode.Accepted;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error sending email: {ex.Message}");
                return false;
            }
        }
    }
}