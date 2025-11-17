using Xunit;
using Moq;
using FluentAssertions;
using API.Managers;
using API.DbContext;
using API.Services;
using System.Threading.Tasks;

namespace API.Tests.Managers
{
    public class AccountManagerTests
    {
        private readonly Mock<AccountDbContext> _mockDbContext;
        private readonly Mock<ForgotPasswordService> _mockForgotPasswordService;
        private readonly AccountManager _accountManager;

        public AccountManagerTests()
        {
            _mockDbContext = new Mock<AccountDbContext>("connectionString");
            var mockEmailService = new Mock<EmailService>("api-key");
            _mockForgotPasswordService = new Mock<ForgotPasswordService>(_mockDbContext.Object, mockEmailService.Object);
            _accountManager = new AccountManager(_mockDbContext.Object, _mockForgotPasswordService.Object);
        }

        [Fact]
        public async Task GeneratePasswordResetToken_WithValidEmail_ReturnsToken()
        {
            // Arrange
            var email = "john@example.com";
            var token = new byte[] { 1, 2, 3, 4 };
            _mockForgotPasswordService.Setup(x => x.GeneratePasswordResetToken(email)).ReturnsAsync(token);

            // Act
            var result = await _accountManager.GeneratePasswordResetToken(email);

            // Assert
            result.Should().NotBeNull();
            result.Should().BeEquivalentTo(token);
        }

        [Fact]
        public async Task GeneratePasswordResetToken_WithInvalidEmail_ReturnsNull()
        {
            // Arrange
            var email = "nonexistent@example.com";
            _mockForgotPasswordService.Setup(x => x.GeneratePasswordResetToken(email)).ReturnsAsync((byte[])null);

            // Act
            var result = await _accountManager.GeneratePasswordResetToken(email);

            // Assert
            result.Should().BeNull();
        }

        [Fact]
        public async Task ChangePassword_WithValidData_ReturnsTrue()
        {
            // Arrange
            var passwordHash = "hashedpassword";
            var email = "john@example.com";
            _mockDbContext.Setup(x => x.ChangePassword(passwordHash, email)).ReturnsAsync(true);

            // Act
            var result = await _accountManager.ChangePassword(passwordHash, email);

            // Assert
            result.Should().BeTrue();
        }

        [Fact]
        public async Task ChangePassword_WithInvalidData_ReturnsFalse()
        {
            // Arrange
            var passwordHash = "hashedpassword";
            var email = "nonexistent@example.com";
            _mockDbContext.Setup(x => x.ChangePassword(passwordHash, email)).ReturnsAsync(false);

            // Act
            var result = await _accountManager.ChangePassword(passwordHash, email);

            // Assert
            result.Should().BeFalse();
        }

        [Fact]
        public async Task VerifyPasswordResetToken_WithValidToken_ReturnsTrue()
        {
            // Arrange
            var token = "validtoken";
            var email = "john@example.com";
            _mockForgotPasswordService.Setup(x => x.VerifyPasswordResetToken(token, email)).ReturnsAsync(true);

            // Act
            var result = await _accountManager.VerifyPasswordResetToken(token, email);

            // Assert
            result.Should().BeTrue();
        }

        [Fact]
        public async Task VerifyPasswordResetToken_WithInvalidToken_ReturnsFalse()
        {
            // Arrange
            var token = "invalidtoken";
            var email = "john@example.com";
            _mockForgotPasswordService.Setup(x => x.VerifyPasswordResetToken(token, email)).ReturnsAsync(false);

            // Act
            var result = await _accountManager.VerifyPasswordResetToken(token, email);

            // Assert
            result.Should().BeFalse();
        }
    }
}

