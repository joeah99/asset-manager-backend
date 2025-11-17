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
    public class AssetManagerTests
    {
        private readonly Mock<AssetDbContext> _mockAssetDbContext;
        private readonly Mock<ValuationDbContext> _mockValuationDbContext;
        private readonly Mock<AssetDepreciationScheduleDbContext> _mockDepreciationDbContext;
        private readonly Mock<AssetValuationService> _mockValuationService;
        private readonly Mock<AssetDepreciationManager> _mockDepreciationManager;
        private readonly AssetManager _assetManager;

        public AssetManagerTests()
        {
            _mockAssetDbContext = new Mock<AssetDbContext>("connectionString");
            _mockValuationDbContext = new Mock<ValuationDbContext>("connectionString");
            _mockDepreciationDbContext = new Mock<AssetDepreciationScheduleDbContext>("connectionString");
            _mockValuationService = new Mock<AssetValuationService>(null, null, null);
            _mockDepreciationManager = new Mock<AssetDepreciationManager>(null, null);
            _assetManager = new AssetManager(
                _mockAssetDbContext.Object,
                _mockValuationDbContext.Object,
                _mockValuationService.Object,
                _mockDepreciationManager.Object,
                _mockDepreciationDbContext.Object
            );
        }

        [Fact]
        public async Task GetAssets_WithValidUserId_ReturnsAssets()
        {
            // Arrange
            var userId = 1L;
            var assets = new List<AssetDTO>
            {
                new AssetDTO { AssetId = 1, UserId = userId, Type = "Equipment" }
            };

            _mockAssetDbContext.Setup(x => x.GetAssetsAsync(userId)).ReturnsAsync(assets);
            _mockValuationDbContext.Setup(x => x.GetAdjustedForcedLiquidationAsync((int)userId)).ReturnsAsync(new List<AdjustedForcedLiquidationDTO>());
            _mockDepreciationDbContext.Setup(x => x.GetAssetDepreciationAsync(userId)).ReturnsAsync(new List<AssetDepreciationScheduleDTO>());

            // Act
            var result = await _assetManager.GetAssets(userId);

            // Assert
            result.Should().NotBeNull();
            result.Count.Should().Be(1);
        }

        [Fact]
        public async Task CreateAsset_WithValidEquipment_ReturnsCreatedAsset()
        {
            // Arrange
            var asset = new AssetDTO
            {
                UserId = 1,
                Type = "Equipment",
                Manufacturer = "Caterpillar",
                Model = "CAT 320",
                ModelYear = "2020",
                Usage = 1000,
                Condition = "Good",
                Country = "USA",
                State = "CA",
                BookValue = 50000
            };

            var createdAsset = new AssetDTO
            {
                AssetId = 1,
                UserId = 1,
                Type = "Equipment"
            };

            var equipmentValuation = new EquipmentValuationDTO
            {
                AdjustedForcedLiquidationValue = 45000
            };

            _mockAssetDbContext.Setup(x => x.GetAssetAsync(asset.UserId, asset)).ReturnsAsync((AssetDTO)null);
            _mockAssetDbContext.Setup(x => x.CreateAssetAsync(asset)).ReturnsAsync(createdAsset);
            _mockValuationService.Setup(x => x.GetEquipmentValuationAsync(
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(),
                It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>()))
                .ReturnsAsync(equipmentValuation);
            _mockValuationDbContext.Setup(x => x.InsertEquipmentValuationAsync(It.IsAny<EquipmentValuationDTO>(), It.IsAny<long>())).Returns(Task.CompletedTask);
            _mockDepreciationManager.Setup(x => x.CreateAssetDepreciationSchedule(It.IsAny<AssetDTO>())).ReturnsAsync(createdAsset);

            // Act
            var result = await _assetManager.CreateAsset(asset);

            // Assert
            result.Should().NotBeNull();
            result.AssetId.Should().Be(1);
        }

        [Fact]
        public async Task CreateAsset_WithDuplicateAsset_ReturnsNull()
        {
            // Arrange
            var asset = new AssetDTO
            {
                UserId = 1,
                Type = "Equipment"
            };

            var existingAsset = new AssetDTO { AssetId = 1, UserId = 1 };
            _mockAssetDbContext.Setup(x => x.GetAssetAsync(asset.UserId, asset)).ReturnsAsync(existingAsset);

            // Act
            var result = await _assetManager.CreateAsset(asset);

            // Assert
            result.Should().BeNull();
        }

        [Fact]
        public async Task DeleteAsset_WithValidAsset_CallsDeleteMethod()
        {
            // Arrange
            var asset = new AssetDTO
            {
                AssetId = 1,
                UserId = 1
            };

            _mockAssetDbContext.Setup(x => x.DeleteAssetAsync(asset)).Returns(Task.CompletedTask);

            // Act
            await _assetManager.DeleteAsset(asset);

            // Assert
            _mockAssetDbContext.Verify(x => x.DeleteAssetAsync(asset), Times.Once);
        }
    }
}

