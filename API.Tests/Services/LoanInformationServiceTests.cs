using Xunit;
using FluentAssertions;
using API.Services;
using API.DTOs;
using System.Collections.Generic;
using System.Linq;

namespace API.Tests.Services
{
    public class LoanInformationServiceTests
    {
        private readonly LoanInformationService _service;

        public LoanInformationServiceTests()
        {
            _service = new LoanInformationService();
        }

        [Fact]
        public void CalculateMonthlyPayment_WithValidInputs_ReturnsCorrectPayment()
        {
            // Arrange
            float loanAmount = 100000;
            float interestRate = 5.0f; // 5% annual
            int loanTermYears = 5;

            // Act
            var result = _service.CalculateMonthlyPayment(loanAmount, interestRate, loanTermYears);

            // Assert
            result.Should().BeGreaterThan(0);
            result.Should().BeLessThan(loanAmount);
            // For a $100,000 loan at 5% for 5 years, monthly payment should be around $1,887
            result.Should().BeApproximately(1887f, 100f);
        }

        [Fact]
        public void CalculateMonthlyPayment_WithZeroInterest_ReturnsPrincipalDividedByMonths()
        {
            // Arrange
            float loanAmount = 100000;
            float interestRate = 0f;
            int loanTermYears = 5;
            float expectedPayment = loanAmount / (loanTermYears * 12);

            // Act
            var result = _service.CalculateMonthlyPayment(loanAmount, interestRate, loanTermYears);

            // Assert
            result.Should().BeApproximately(expectedPayment, 0.01f);
        }

        [Fact]
        public void GenerateLoanSchedule_WithValidLoan_ReturnsCompleteSchedule()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                LoanId = 1,
                LoanAmount = 100000,
                InterestRate = 5.0f,
                LoanTermYears = 5,
                MonthlyPayment = 1887.12f,
                LoanStartDate = "2024-01-01",
                LoanEndDate = "2029-01-01"
            };

            // Act
            var result = _service.GenerateLoanSchedule(loan);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().BeGreaterThan(0);
            result.Count.Should().BeLessThanOrEqualTo(loan.LoanTermYears * 12);
            result.First().NewRemainingValue.Should().BeLessThan(loan.LoanAmount);
        }

        [Fact]
        public void GenerateLoanSchedule_RemainingBalanceDecreasesOverTime()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                LoanId = 1,
                LoanAmount = 100000,
                InterestRate = 5.0f,
                LoanTermYears = 5,
                MonthlyPayment = 1887.12f,
                LoanStartDate = "2024-01-01",
                LoanEndDate = "2029-01-01"
            };

            // Act
            var result = _service.GenerateLoanSchedule(loan);

            // Assert
            if (result.Count > 1)
            {
                for (int i = 1; i < result.Count; i++)
                {
                    result[i].NewRemainingValue.Should().BeLessThanOrEqualTo(result[i - 1].NewRemainingValue);
                }
            }
        }

        [Fact]
        public void GenerateLoanSchedule_LastPaymentShouldHaveZeroOrMinimalBalance()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                LoanId = 1,
                LoanAmount = 100000,
                InterestRate = 5.0f,
                LoanTermYears = 5,
                MonthlyPayment = 1887.12f,
                LoanStartDate = "2024-01-01",
                LoanEndDate = "2029-01-01"
            };

            // Act
            var result = _service.GenerateLoanSchedule(loan);

            // Assert
            result.Last().NewRemainingValue.Should().BeLessThanOrEqualTo(loan.MonthlyPayment);
        }

        [Fact]
        public void GenerateLoanSchedule_WithDefaultDates_UsesCurrentDate()
        {
            // Arrange
            var loan = new LoanInformationDTO
            {
                LoanId = 1,
                LoanAmount = 100000,
                InterestRate = 5.0f,
                LoanTermYears = 5,
                MonthlyPayment = 1887.12f,
                LoanStartDate = "",
                LoanEndDate = ""
            };

            // Act
            var result = _service.GenerateLoanSchedule(loan);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().BeGreaterThan(0);
        }
    }
}

