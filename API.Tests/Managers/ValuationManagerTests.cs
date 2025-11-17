using Xunit;
using Moq;
using FluentAssertions;
using API.Managers;
using API.DbContext;
using API.DTOs;
using System.Collections.Generic;
using System.Threading.Tasks;
using System;

namespace API.Tests.Managers
{
    public class ValuationManagerTests
    {
        private readonly Mock<ValuationDbContext> _mockValuationDbContext;
        private readonly ValuationManager _valuationManager;

        public ValuationManagerTests()
        {
            _mockValuationDbContext = new Mock<ValuationDbContext>("connectionString");
            _valuationManager = new ValuationManager(_mockValuationDbContext.Object);
        }

        [Fact]
        public async Task GetEquipmentValuations_WithValidUserId_ReturnsValuations()
        {
            // Arrange
            var userId = 1;
            var valuations = new List<EquipmentValuationDTO>
            {
                new EquipmentValuationDTO
                {
                    AssetId = 1,
                    AdjustedFairMarketValue = 50000,
                    AdjustedForcedLiquidationValue = 45000
                }
            };

            _mockValuationDbContext.Setup(x => x.GetEquipmentValuationsAsync(userId)).ReturnsAsync(valuations);

            // Act
            var result = await _valuationManager.GetEquipmentValuations(userId);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().Be(1);
        }

        [Fact]
        public async Task GetTotalFairMarketValue_WithValidUserId_ReturnsMonthlyTotals()
        {
            // Arrange
            var userId = 1;
            var valuations = new List<EquipmentValuationDTO>
            {
                new EquipmentValuationDTO
                {
                    AssetId = 1,
                    AdjustedFairMarketValue = 50000,
                    ValuationDate = System.DateTime.Now.AddMonths(-1)
                }
            };

            _mockValuationDbContext.Setup(x => x.GetEquipmentValuationsAsync(userId)).ReturnsAsync(valuations);

            // Act
            var result = await _valuationManager.GetTotalFairMarketValue(userId);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().BeGreaterThan(0);
        }

        [Fact]
        public async Task GetTotalAssetValue_WithValidUserId_ReturnsTotalValue()
        {
            // Arrange
            var userId = 1;
            var valuations = new List<EquipmentValuationDTO>
            {
                new EquipmentValuationDTO
                {
                    AssetId = 1,
                    AdjustedFairMarketValue = 50000,
                    ValuationDate = System.DateTime.Now
                }
            };

            _mockValuationDbContext.Setup(x => x.GetEquipmentValuationsAsync(userId)).ReturnsAsync(valuations);

            // Act
            var result = await _valuationManager.GetTotalAssetValue(userId);

            // Assert
            result.Should().NotBeNull();
            result.TotalAssetValue.Should().BeGreaterThan(0);
        }

        [Fact]
        public async Task GetAdjustedForcedLiquidationAsync_WithValidUserId_ReturnsLiquidationData()
        {
            // Arrange
            var userId = 1;
            // The DbContext returns List<AdjustedForcedLiquidation> which the manager transforms to DTOs
            var liquidationData = new List<AdjustedForcedLiquidation>
            {
                new AdjustedForcedLiquidation
                {
                    AssetId = 1,
                    ValuationDate = DateTime.Parse("2024-01-01"),
                    AdjustedForcedLiquidationValue = 45000.0
                }
            };

            _mockValuationDbContext.Setup(x => x.GetAdjustedForcedLiquidationAsync(userId))
                .ReturnsAsync(liquidationData);

            // Act
            var result = await _valuationManager.GetAdjustedForcedLiquidationAsync(userId);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().Be(1);
            result[0].AssetId.Should().Be(1);
            result[0].ValuationDate.Should().Be("2024-01-01");
        }
    }
}

