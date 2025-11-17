using Xunit;
using Moq;
using FluentAssertions;
using API.Controllers;
using API.Managers;
using API.DTOs;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace API.Tests.Controllers
{
    public class LoanInformationControllerTests
    {
        private readonly Mock<LoanManager> _mockLoanManager;
        private readonly LoanInformationController _controller;

        public LoanInformationControllerTests()
        {
            _mockLoanManager = new Mock<LoanManager>(null, null, null);
            _controller = new LoanInformationController(_mockLoanManager.Object);
        }

        [Fact]
        public async Task CreateLoanRecord_WithValidLoan_ReturnsOk()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                UserId = 1,
                AssetId = 1,
                LenderName = "Bank ABC",
                LoanAmount = 100000,
                InterestRate = 5.5,
                LoanTermYears = 5
            };

            var createdLoan = new LoanInformationDTO
            {
                LoanId = 1,
                UserId = 1,
                AssetId = 1,
                LenderName = "Bank ABC",
                LoanAmount = 100000,
                InterestRate = 5.5,
                LoanTermYears = 5
            };

            _mockLoanManager.Setup(x => x.CreateLoan(loan)).ReturnsAsync(createdLoan);

            // Act
            var result = await _controller.CreateLoanRecord(loan);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task CreateLoanRecord_WithInvalidLoan_ReturnsNotFound()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                UserId = 1,
                AssetId = 1,
                LenderName = "Bank ABC",
                LoanAmount = 100000
            };

            _mockLoanManager.Setup(x => x.CreateLoan(loan)).ReturnsAsync((LoanInformationDTO)null);

            // Act
            var result = await _controller.CreateLoanRecord(loan);

            // Assert
            var notFoundResult = result.Result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }

        [Fact]
        public async Task GetLoans_WithValidUserId_ReturnsOk()
        {
            // Arrange
            var userId = 1L;
            var loans = new List<LoanInformationDTO>
            {
                new LoanInformationDTO
                {
                    LoanId = 1,
                    UserId = userId,
                    AssetId = 1,
                    LenderName = "Bank ABC",
                    LoanAmount = 100000
                }
            };

            _mockLoanManager.Setup(x => x.GetLoans(userId)).ReturnsAsync(loans);

            // Act
            var result = await _controller.GetLoans(userId);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
            okResult.Value.Should().BeEquivalentTo(loans);
        }

        [Fact]
        public async Task GetLoans_WithNoLoans_ReturnsNotFound()
        {
            // Arrange
            var userId = 1L;
            _mockLoanManager.Setup(x => x.GetLoans(userId)).ReturnsAsync((List<LoanInformationDTO>)null);

            // Act
            var result = await _controller.GetLoans(userId);

            // Assert
            var notFoundResult = result.Result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }

        [Fact]
        public async Task UpdateLoan_WithValidLoan_ReturnsOk()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                LoanId = 1,
                UserId = 1,
                AssetId = 1,
                LenderName = "Bank ABC Updated",
                LoanAmount = 120000,
                InterestRate = 6.0,
                LoanTermYears = 5
            };

            var updatedLoan = new LoanInformationDTO
            {
                LoanId = 1,
                UserId = 1,
                AssetId = 1,
                LenderName = "Bank ABC Updated",
                LoanAmount = 120000
            };

            _mockLoanManager.Setup(x => x.UpdateLoan(loan)).ReturnsAsync(updatedLoan);

            // Act
            var result = await _controller.UpdateLoan(loan);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task UpdateLoan_WithInvalidLoan_ReturnsInternalServerError()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                LoanId = 999,
                UserId = 1
            };

            _mockLoanManager.Setup(x => x.UpdateLoan(loan)).ReturnsAsync((LoanInformationDTO)null);

            // Act
            var result = await _controller.UpdateLoan(loan);

            // Assert
            var statusCodeResult = result.Result as ObjectResult;
            statusCodeResult.Should().NotBeNull();
            statusCodeResult.StatusCode.Should().Be(500);
        }

        [Fact]
        public async Task DeleteLoan_WithValidLoanId_ReturnsOk()
        {
            // Arrange
            var loanId = 1L;
            _mockLoanManager.Setup(x => x.DeleteLoan(loanId)).ReturnsAsync(true);

            // Act
            var result = await _controller.DeleteLoan(loanId);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task DeleteLoan_WithInvalidLoanId_ReturnsInternalServerError()
        {
            // Arrange
            var loanId = 999L;
            _mockLoanManager.Setup(x => x.DeleteLoan(loanId)).ReturnsAsync(false);

            // Act
            var result = await _controller.DeleteLoan(loanId);

            // Assert
            var statusCodeResult = result as ObjectResult;
            statusCodeResult.Should().NotBeNull();
            statusCodeResult.StatusCode.Should().Be(500);
        }
    }
}

