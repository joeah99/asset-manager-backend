using Xunit;
using Moq;
using FluentAssertions;
using API.Controllers;
using API.Managers;
using API.DTOs;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace API.Tests.Controllers
{
    public class ValuationControllerTests
    {
        private readonly Mock<ILogger<ValuationController>> _mockLogger;
        private readonly Mock<AssetManager> _mockAssetManager;
        private readonly Mock<ValuationManager> _mockValuationManager;
        private readonly ValuationController _controller;

        public ValuationControllerTests()
        {
            _mockLogger = new Mock<ILogger<ValuationController>>();
            _mockAssetManager = new Mock<AssetManager>(null, null, null, null, null);
            _mockValuationManager = new Mock<ValuationManager>(null);
            _controller = new ValuationController(_mockLogger.Object, _mockAssetManager.Object, _mockValuationManager.Object);
        }

        [Fact]
        public async Task GetAssetValuations_WithValidUserId_ReturnsOk()
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

            _mockValuationManager.Setup(x => x.GetEquipmentValuations(userId)).ReturnsAsync(valuations);

            // Act
            var result = await _controller.GetAssetValuations(userId);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
            okResult.Value.Should().BeEquivalentTo(valuations);
        }

        [Fact]
        public async Task GetAssetValuations_WithNoValuations_ReturnsNotFound()
        {
            // Arrange
            var userId = 1;
            _mockValuationManager.Setup(x => x.GetEquipmentValuations(userId)).ReturnsAsync((List<EquipmentValuationDTO>)null);

            // Act
            var result = await _controller.GetAssetValuations(userId);

            // Assert
            var notFoundResult = result.Result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }

        [Fact]
        public async Task GetTotalFairMarketValue_WithValidUserId_ReturnsOk()
        {
            // Arrange
            var userId = 1;
            var totalFMV = new List<MonthlyTotalFMVDTO>
            {
                new MonthlyTotalFMVDTO
                {
                    Month = "January",
                    TotalFairMarketValue = 100000,
                    NumberOfAssets = 5
                }
            };

            _mockValuationManager.Setup(x => x.GetTotalFairMarketValue(userId)).ReturnsAsync(totalFMV);

            // Act
            var result = await _controller.GetTotalFairMarketValue(userId);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task GetTotalFairMarketValue_WithNoData_ReturnsNotFound()
        {
            // Arrange
            var userId = 1;
            _mockValuationManager.Setup(x => x.GetTotalFairMarketValue(userId)).ReturnsAsync((List<MonthlyTotalFMVDTO>)null);

            // Act
            var result = await _controller.GetTotalFairMarketValue(userId);

            // Assert
            var notFoundResult = result.Result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }

        [Fact]
        public async Task GetTotalAssetValue_WithValidUserId_ReturnsOk()
        {
            // Arrange
            var userId = 1;
            var totalAssetValue = new TotalAssetValueDTO
            {
                TotalAssetValue = 500000,
                percentChangePastYear = 10
            };

            _mockValuationManager.Setup(x => x.GetTotalAssetValue(userId)).ReturnsAsync(totalAssetValue);

            // Act
            var result = await _controller.GetTotalAssetValue(userId);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task GetTotalAssetValue_WithNoData_ReturnsNotFound()
        {
            // Arrange
            var userId = 1;
            _mockValuationManager.Setup(x => x.GetTotalAssetValue(userId)).ReturnsAsync((TotalAssetValueDTO)null);

            // Act
            var result = await _controller.GetTotalAssetValue(userId);

            // Assert
            var notFoundResult = result.Result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }

        [Fact]
        public async Task GetAdjustedForcedLiquidation_WithValidUserId_ReturnsOk()
        {
            // Arrange
            var userId = 1;
            var adjustedLiquidation = new List<AdjustedForcedLiquidationDTO>
            {
                new AdjustedForcedLiquidationDTO
                {
                    AssetId = 1,
                    ValuationDate = "2024-01-01",
                    AdjustedForcedLiquidationValue = 45000
                }
            };

            _mockValuationManager.Setup(x => x.GetAdjustedForcedLiquidationAsync(userId)).ReturnsAsync(adjustedLiquidation);

            // Act
            var result = await _controller.GetAdjustedForcedLiquidation(userId);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task GetAdjustedForcedLiquidation_WithNoData_ReturnsNotFound()
        {
            // Arrange
            var userId = 1;
            _mockValuationManager.Setup(x => x.GetAdjustedForcedLiquidationAsync(userId)).ReturnsAsync((List<AdjustedForcedLiquidationDTO>)null);

            // Act
            var result = await _controller.GetAdjustedForcedLiquidation(userId);

            // Assert
            var notFoundResult = result.Result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }
    }
}

