using Xunit;
using Moq;
using FluentAssertions;
using API.Managers;
using API.DbContext;
using API.Services;
using API.DTOs;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace API.Tests.Managers
{
    public class LoanManagerTests
    {
        private readonly Mock<LoanInformationDbContext> _mockLoanDbContext;
        private readonly Mock<LoanProjectedPaymentsDbContext> _mockPaymentsDbContext;
        private readonly Mock<LoanInformationService> _mockLoanService;
        private readonly LoanManager _loanManager;

        public LoanManagerTests()
        {
            _mockLoanDbContext = new Mock<LoanInformationDbContext>("connectionString");
            _mockPaymentsDbContext = new Mock<LoanProjectedPaymentsDbContext>("connectionString");
            _mockLoanService = new Mock<LoanInformationService>();
            _loanManager = new LoanManager(
                _mockLoanDbContext.Object,
                _mockPaymentsDbContext.Object,
                _mockLoanService.Object
            );
        }

        [Fact]
        public async Task GetLoans_WithValidUserId_ReturnsLoans()
        {
            // Arrange
            var userId = 1L;
            var loans = new List<LoanInformationDTO>
            {
                new LoanInformationDTO
                {
                    LoanId = 1,
                    UserId = userId,
                    LoanAmount = 100000
                }
            };

            _mockLoanDbContext.Setup(x => x.GetLoansAsync(userId)).ReturnsAsync(loans);
            _mockPaymentsDbContext.Setup(x => x.GetLoanProjectedPaymentsByUserIdAsync(userId))
                .ReturnsAsync(new List<LoanProjectedPaymentsDTO>());

            // Act
            var result = await _loanManager.GetLoans(userId);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().Be(1);
        }

        [Fact]
        public async Task CreateLoan_WithValidLoan_ReturnsCreatedLoan()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                UserId = 1,
                AssetId = 1,
                LenderName = "Bank ABC",
                LoanAmount = 100000,
                InterestRate = 5.5f,
                LoanTermYears = 5
            };

            var createdLoan = new LoanInformationDTO
            {
                LoanId = 1,
                UserId = 1,
                LoanAmount = 100000,
                InterestRate = 5.5f,
                LoanTermYears = 5
            };

            var loanSchedule = new List<LoanScheduleDTO>
            {
                new LoanScheduleDTO
                {
                    LoanPaymentDate = "2024-02-01",
                    NewRemainingValue = 95000
                }
            };

            _mockLoanService.Setup(x => x.CalculateMonthlyPayment(
                loan.LoanAmount, loan.InterestRate, loan.LoanTermYears)).Returns(1887.12f);
            _mockLoanDbContext.Setup(x => x.CreateLoanRecordAsync(loan)).ReturnsAsync(createdLoan);
            _mockLoanService.Setup(x => x.GenerateLoanSchedule(createdLoan)).Returns(loanSchedule);
            _mockPaymentsDbContext.Setup(x => x.CreateLoanProjectedPaymentsAsync(It.IsAny<LoanProjectedPaymentsDTO>()))
                .Returns(Task.CompletedTask);

            // Act
            var result = await _loanManager.CreateLoan(loan);

            // Assert
            result.Should().NotBeNull();
            result.LoanId.Should().Be(1);
        }

        [Fact]
        public async Task DeleteLoan_WithValidLoanId_ReturnsTrue()
        {
            // Arrange
            var loanId = 1L;
            _mockLoanDbContext.Setup(x => x.DeleteLoanRecordAsync(loanId)).ReturnsAsync(true);

            // Act
            var result = await _loanManager.DeleteLoan(loanId);

            // Assert
            result.Should().BeTrue();
        }
    }
}

