using Xunit;
using FluentAssertions;
using API.Services;
using API.DTOs;
using System.Collections.Generic;
using System.Linq;

namespace API.Tests.Services
{
    public class AssetDepreciationServiceTests
    {
        private readonly AssetDepreciationService _service;

        public AssetDepreciationServiceTests()
        {
            _service = new AssetDepreciationService();
        }

        [Fact]
        public void StraightLineDepreciation_WithValidInputs_ReturnsCorrectSchedule()
        {
            // Arrange
            double initialCost = 100000;
            double salvageValue = 10000;
            int usefulLife = 5;

            // Act
            var result = _service.StraightLineDepreciation(initialCost, salvageValue, usefulLife);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().Be(usefulLife * 12); // 5 years * 12 months = 60 months
            result.First().NewBookValue.Should().BeLessThan(initialCost);
            result.Last().NewBookValue.Should().BeApproximately((float)salvageValue, 0.01f);
        }

        [Fact]
        public void StraightLineDepreciation_CalculatesCorrectMonthlyDepreciation()
        {
            // Arrange
            double initialCost = 100000;
            double salvageValue = 10000;
            int usefulLife = 5;
            double expectedAnnualDepreciation = (initialCost - salvageValue) / usefulLife;
            double expectedMonthlyDepreciation = expectedAnnualDepreciation / 12;

            // Act
            var result = _service.StraightLineDepreciation(initialCost, salvageValue, usefulLife);

            // Assert
            if (result.Count > 1)
            {
                var firstMonthValue = result[0].NewBookValue;
                var secondMonthValue = result[1].NewBookValue;
                var actualDepreciation = firstMonthValue - secondMonthValue;
                actualDepreciation.Should().BeApproximately((float)expectedMonthlyDepreciation, 0.01f);
            }
        }

        [Fact]
        public void DecliningBalanceDepreciation_WithValidInputs_ReturnsCorrectSchedule()
        {
            // Arrange
            double initialCost = 100000;
            double salvageValue = 10000;
            int usefulLife = 5;
            double rate = 0.2; // 20%

            // Act
            var result = _service.DecliningBalanceDepreciation(initialCost, salvageValue, usefulLife, rate);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().Be(usefulLife * 12);
            result.First().NewBookValue.Should().BeLessThan(initialCost);
            result.Last().NewBookValue.Should().BeGreaterOrEqualTo((float)salvageValue);
        }

        [Fact]
        public void DoubleDecliningBalanceDepreciation_WithValidInputs_ReturnsCorrectSchedule()
        {
            // Arrange
            double initialCost = 100000;
            double salvageValue = 10000;
            int usefulLife = 5;

            // Act
            var result = _service.DoubleDecliningBalanceDepreciation(initialCost, salvageValue, usefulLife);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().Be(usefulLife * 12);
            result.First().NewBookValue.Should().BeLessThan(initialCost);
            result.Last().NewBookValue.Should().BeGreaterOrEqualTo((float)salvageValue);
        }

        [Fact]
        public void UnitsOfProductionDepreciation_WithValidInputs_ReturnsCorrectSchedule()
        {
            // Arrange
            double initialCost = 100000;
            double salvageValue = 10000;
            int totalUnits = 1000000;
            int unitsProducedPerYear = 200000;

            // Act
            var result = _service.UnitsOfProductionDepreciation(initialCost, salvageValue, totalUnits, unitsProducedPerYear);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().BeGreaterThan(0);
            result.First().NewBookValue.Should().BeLessThan(initialCost);
            result.Last().NewBookValue.Should().BeGreaterOrEqualTo((float)salvageValue);
        }

        [Fact]
        public void ModifiedAcceleratedCostRecoverySystem_WithValidInputs_ReturnsCorrectSchedule()
        {
            // Arrange
            double initialCost = 100000;
            int usefulLife = 5;

            // Act
            var result = _service.ModifiedAcceleratedCostRecoverySystem(initialCost, usefulLife);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().Be(72); // 6 years * 12 months
            result.First().NewBookValue.Should().BeLessThan(initialCost);
        }

        [Fact]
        public void StraightLineDepreciation_BookValueNeverGoesBelowSalvageValue()
        {
            // Arrange
            double initialCost = 100000;
            double salvageValue = 10000;
            int usefulLife = 5;

            // Act
            var result = _service.StraightLineDepreciation(initialCost, salvageValue, usefulLife);

            // Assert
            result.All(r => r.NewBookValue >= salvageValue).Should().BeTrue();
        }
    }
}

