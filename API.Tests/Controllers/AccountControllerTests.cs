using Xunit;
using Moq;
using FluentAssertions;
using API.Controllers;
using API.DbContext;
using API.Managers;
using API.DTOs;
using API.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System.Threading.Tasks;

namespace API.Tests.Controllers
{
    public class AccountControllerTests
    {
        private readonly Mock<AccountDbContext> _mockDbContext;
        private readonly Mock<ForgotPasswordService> _mockForgotPasswordService;
        private readonly AccountManager _accountManager;
        private readonly AccountController _controller;

        public AccountControllerTests()
        {
            _mockDbContext = new Mock<AccountDbContext>("connectionString");
            var mockEmailService = new Mock<EmailService>("api-key");
            _mockForgotPasswordService = new Mock<ForgotPasswordService>(_mockDbContext.Object, mockEmailService.Object);
            _accountManager = new AccountManager(_mockDbContext.Object, _mockForgotPasswordService.Object);
            _controller = new AccountController(_mockDbContext.Object, _accountManager);
        }

        [Fact]
        public async Task Register_WithValidData_ReturnsOk()
        {
            // Arrange
            var registerDto = new RegisterDto
            {
                FirstName = "John",
                LastName = "Doe",
                Username = "johndoe",
                Email = "john@example.com",
                Password = "Password123!"
            };

            _mockDbContext.Setup(x => x.UserExists(registerDto.Email)).ReturnsAsync(false);
            _mockDbContext.Setup(x => x.UsernameExists(registerDto.Username)).ReturnsAsync(false);
            _mockDbContext.Setup(x => x.RegisterUser(It.IsAny<AppUser>())).ReturnsAsync(new AppUser
            {
                UserId = 1,
                FullName = "John Doe",
                Username = "johndoe",
                Email = "john@example.com"
            });

            // Act
            var result = await _controller.Register(registerDto);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task Register_WithExistingEmail_ReturnsBadRequest()
        {
            // Arrange
            var registerDto = new RegisterDto
            {
                FirstName = "John",
                LastName = "Doe",
                Username = "johndoe",
                Email = "existing@example.com",
                Password = "Password123!"
            };

            _mockDbContext.Setup(x => x.UserExists(registerDto.Email)).ReturnsAsync(true);

            // Act
            var result = await _controller.Register(registerDto);

            // Assert
            var badRequestResult = result.Result as BadRequestObjectResult;
            badRequestResult.Should().NotBeNull();
            badRequestResult.StatusCode.Should().Be(400);
        }

        [Fact]
        public async Task Register_WithExistingUsername_ReturnsBadRequest()
        {
            // Arrange
            var registerDto = new RegisterDto
            {
                FirstName = "John",
                LastName = "Doe",
                Username = "existinguser",
                Email = "john@example.com",
                Password = "Password123!"
            };

            _mockDbContext.Setup(x => x.UserExists(registerDto.Email)).ReturnsAsync(false);
            _mockDbContext.Setup(x => x.UsernameExists(registerDto.Username)).ReturnsAsync(true);

            // Act
            var result = await _controller.Register(registerDto);

            // Assert
            var badRequestResult = result.Result as BadRequestObjectResult;
            badRequestResult.Should().NotBeNull();
            badRequestResult.StatusCode.Should().Be(400);
        }

        [Fact]
        public async Task Login_WithValidCredentials_ReturnsOk()
        {
            // Arrange
            var loginDto = new LoginDto
            {
                Email = "john@example.com",
                Password = "Password123!"
            };

            var user = new AppUser
            {
                UserId = 1,
                FullName = "John Doe",
                Username = "johndoe",
                Email = "john@example.com"
            };

            _mockDbContext.Setup(x => x.UserExists(loginDto.Email)).ReturnsAsync(true);
            _mockDbContext.Setup(x => x.IsPasswordValid(loginDto)).ReturnsAsync(true);
            _mockDbContext.Setup(x => x.GetUserByUsername(loginDto.Email)).ReturnsAsync(user);

            // Act
            var result = await _controller.Login(loginDto);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task Login_WithInvalidPassword_ReturnsUnauthorized()
        {
            // Arrange
            var loginDto = new LoginDto
            {
                Email = "john@example.com",
                Password = "WrongPassword"
            };

            _mockDbContext.Setup(x => x.UserExists(loginDto.Email)).ReturnsAsync(true);
            _mockDbContext.Setup(x => x.IsPasswordValid(loginDto)).ReturnsAsync(false);

            // Act
            var result = await _controller.Login(loginDto);

            // Assert
            var unauthorizedResult = result.Result as UnauthorizedObjectResult;
            unauthorizedResult.Should().NotBeNull();
            unauthorizedResult.StatusCode.Should().Be(401);
        }

        [Fact]
        public async Task Login_WithNonExistentUser_ReturnsBadRequest()
        {
            // Arrange
            var loginDto = new LoginDto
            {
                Email = "nonexistent@example.com",
                Password = "Password123!"
            };

            _mockDbContext.Setup(x => x.UserExists(loginDto.Email)).ReturnsAsync(false);

            // Act
            var result = await _controller.Login(loginDto);

            // Assert
            var badRequestResult = result.Result as BadRequestObjectResult;
            badRequestResult.Should().NotBeNull();
            badRequestResult.StatusCode.Should().Be(400);
        }

        [Fact]
        public async Task CheckIfUserNameExists_WithExistingUsername_ReturnsTrue()
        {
            // Arrange
            var username = "existinguser";
            _mockDbContext.Setup(x => x.UsernameExists(username)).ReturnsAsync(true);

            // Act
            var result = await _controller.CheckIfUserNameExists(username);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.Value.Should().Be(true);
        }

        [Fact]
        public async Task CheckIfUserNameExists_WithNonExistentUsername_ReturnsFalse()
        {
            // Arrange
            var username = "newuser";
            _mockDbContext.Setup(x => x.UsernameExists(username)).ReturnsAsync(false);

            // Act
            var result = await _controller.CheckIfUserNameExists(username);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.Value.Should().Be(false);
        }

        [Fact]
        public async Task DeleteUser_WithExistingUser_ReturnsOk()
        {
            // Arrange
            var email = "john@example.com";
            _mockDbContext.Setup(x => x.UserExists(email)).ReturnsAsync(true);
            _mockDbContext.Setup(x => x.DeleteUser(email)).ReturnsAsync(true);

            // Act
            var result = await _controller.DeleteUser(email);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task DeleteUser_WithNonExistentUser_ReturnsNotFound()
        {
            // Arrange
            var email = "nonexistent@example.com";
            _mockDbContext.Setup(x => x.UserExists(email)).ReturnsAsync(false);

            // Act
            var result = await _controller.DeleteUser(email);

            // Assert
            var notFoundResult = result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }

        [Fact]
        public async Task UpdateUser_WithValidUser_ReturnsOk()
        {
            // Arrange
            var user = new AppUser
            {
                UserId = 1,
                FullName = "John Doe Updated",
                Username = "johndoe",
                Email = "john@example.com"
            };

            _mockDbContext.Setup(x => x.UpdateUser(user)).ReturnsAsync(true);

            // Act
            var result = await _controller.UpdateUser(user);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task ForgotPassword_WithValidEmail_ReturnsOk()
        {
            // Arrange
            var email = "john@example.com";
            var token = new byte[] { 1, 2, 3, 4 };
            _mockForgotPasswordService.Setup(x => x.GeneratePasswordResetToken(email)).ReturnsAsync(token);

            // Act
            var result = await _controller.ForgotPassword(email);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task ForgotPassword_WithInvalidEmail_ReturnsInternalServerError()
        {
            // Arrange
            var email = "nonexistent@example.com";
            _mockForgotPasswordService.Setup(x => x.GeneratePasswordResetToken(email)).ReturnsAsync((byte[])null);

            // Act
            var result = await _controller.ForgotPassword(email);

            // Assert
            var statusCodeResult = result as ObjectResult;
            statusCodeResult.Should().NotBeNull();
            statusCodeResult.StatusCode.Should().Be(500);
        }

        [Fact]
        public async Task EnterResetToken_WithValidToken_ReturnsOk()
        {
            // Arrange
            var verifyTokenDto = new VerifyResetTokenDTO
            {
                Token = "validtoken",
                Email = "john@example.com"
            };

            _mockForgotPasswordService.Setup(x => x.VerifyPasswordResetToken(verifyTokenDto.Token, verifyTokenDto.Email)).ReturnsAsync(true);

            // Act
            var result = await _controller.EnterResetToken(verifyTokenDto);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task EnterResetToken_WithInvalidToken_ReturnsInternalServerError()
        {
            // Arrange
            var verifyTokenDto = new VerifyResetTokenDTO
            {
                Token = "invalidtoken",
                Email = "john@example.com"
            };

            _mockForgotPasswordService.Setup(x => x.VerifyPasswordResetToken(verifyTokenDto.Token, verifyTokenDto.Email)).ReturnsAsync(false);

            // Act
            var result = await _controller.EnterResetToken(verifyTokenDto);

            // Assert
            var statusCodeResult = result as ObjectResult;
            statusCodeResult.Should().NotBeNull();
            statusCodeResult.StatusCode.Should().Be(500);
        }

        [Fact]
        public async Task ChangePassword_WithValidData_ReturnsOk()
        {
            // Arrange
            var changePasswordDto = new ChangePasswordDTO
            {
                Email = "john@example.com",
                Password = "NewPassword123!"
            };

            _mockDbContext.Setup(x => x.ChangePassword(It.IsAny<string>(), changePasswordDto.Email)).ReturnsAsync(true);

            // Act
            var result = await _controller.ChangePassword(changePasswordDto);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task SaveColumnPreferences_WithValidData_ReturnsOk()
        {
            // Arrange
            var preferences = new ColumnPreferencesDto
            {
                UserId = 1,
                Preferences = "{\"columns\": [\"AssetId\", \"Type\", \"Manufacturer\"]}"
            };

            _mockDbContext.Setup(x => x.SaveUserColumnPreferences(preferences.UserId, preferences.Preferences)).ReturnsAsync(true);

            // Act
            var result = await _controller.SaveColumnPreferences(preferences);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task GetColumnPreferences_WithValidUserId_ReturnsOk()
        {
            // Arrange
            var userId = 1L;
            var preferences = "{\"columns\": [\"AssetId\", \"Type\", \"Manufacturer\"]}";
            _mockDbContext.Setup(x => x.GetUserColumnPreferences(userId)).ReturnsAsync(preferences);

            // Act
            var result = await _controller.GetColumnPreferences(userId);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task GetColumnPreferences_WithNonExistentUserId_ReturnsNotFound()
        {
            // Arrange
            var userId = 999L;
            _mockDbContext.Setup(x => x.GetUserColumnPreferences(userId)).ReturnsAsync((string)null);

            // Act
            var result = await _controller.GetColumnPreferences(userId);

            // Assert
            var notFoundResult = result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }
    }
}

