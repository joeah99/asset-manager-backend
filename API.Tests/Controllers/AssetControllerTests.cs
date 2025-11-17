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
    public class AssetControllerTests
    {
        private readonly Mock<ILogger<AssetController>> _mockLogger;
        private readonly Mock<AssetManager> _mockAssetManager;
        private readonly AssetController _controller;

        public AssetControllerTests()
        {
            _mockLogger = new Mock<ILogger<AssetController>>();
            _mockAssetManager = new Mock<AssetManager>(null, null, null, null, null);
            _controller = new AssetController(_mockLogger.Object, _mockAssetManager.Object);
        }

        [Fact]
        public async Task GetUserAssets_WithValidUserId_ReturnsOk()
        {
            // Arrange
            var userId = 1L;
            var assets = new List<AssetDTO>
            {
                new AssetDTO
                {
                    AssetId = 1,
                    UserId = userId,
                    Type = "Equipment",
                    Manufacturer = "Caterpillar",
                    Model = "CAT 320",
                    ModelYear = "2020"
                }
            };

            _mockAssetManager.Setup(x => x.GetAssets(userId)).ReturnsAsync(assets);

            // Act
            var result = await _controller.GetUserAssets(userId);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
            okResult.Value.Should().BeEquivalentTo(assets);
        }

        [Fact]
        public async Task GetUserAssets_WithNoAssets_ReturnsNotFound()
        {
            // Arrange
            var userId = 1L;
            _mockAssetManager.Setup(x => x.GetAssets(userId)).ReturnsAsync((List<AssetDTO>)null);

            // Act
            var result = await _controller.GetUserAssets(userId);

            // Assert
            var notFoundResult = result.Result as NotFoundObjectResult;
            notFoundResult.Should().NotBeNull();
            notFoundResult.StatusCode.Should().Be(404);
        }

        [Fact]
        public async Task CreateAsset_WithValidAsset_ReturnsOk()
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
                Type = "Equipment",
                Manufacturer = "Caterpillar",
                Model = "CAT 320",
                ModelYear = "2020"
            };

            _mockAssetManager.Setup(x => x.CreateAsset(asset)).ReturnsAsync(createdAsset);

            // Act
            var result = await _controller.CreateAsset(asset);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task CreateAsset_WithDuplicateAsset_ReturnsBadRequest()
        {
            // Arrange
            var asset = new AssetDTO
            {
                UserId = 1,
                Type = "Equipment",
                Manufacturer = "Caterpillar",
                Model = "CAT 320",
                ModelYear = "2020"
            };

            _mockAssetManager.Setup(x => x.CreateAsset(asset)).ReturnsAsync((AssetDTO)null);

            // Act
            var result = await _controller.CreateAsset(asset);

            // Assert
            var badRequestResult = result.Result as BadRequestObjectResult;
            badRequestResult.Should().NotBeNull();
            badRequestResult.StatusCode.Should().Be(400);
        }

        [Fact]
        public async Task DeleteAsset_WithValidAsset_ReturnsOk()
        {
            // Arrange
            var asset = new AssetDTO
            {
                AssetId = 1,
                UserId = 1
            };

            _mockAssetManager.Setup(x => x.DeleteAsset(asset)).Returns(Task.CompletedTask);

            // Act
            var result = await _controller.DeleteAsset(asset);

            // Assert
            var okResult = result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task DeleteAsset_WithException_ReturnsInternalServerError()
        {
            // Arrange
            var asset = new AssetDTO
            {
                AssetId = 1,
                UserId = 1
            };

            _mockAssetManager.Setup(x => x.DeleteAsset(asset)).ThrowsAsync(new Exception("Database error"));

            // Act
            var result = await _controller.DeleteAsset(asset);

            // Assert
            var statusCodeResult = result as ObjectResult;
            statusCodeResult.Should().NotBeNull();
            statusCodeResult.StatusCode.Should().Be(500);
        }

        [Fact]
        public async Task UpdateAsset_WithValidAsset_ReturnsOk()
        {
            // Arrange
            var asset = new AssetDTO
            {
                AssetId = 1,
                UserId = 1,
                Type = "Equipment",
                Manufacturer = "Caterpillar",
                Model = "CAT 320",
                ModelYear = "2020",
                BookValue = 55000
            };

            var updatedAsset = new AssetDTO
            {
                AssetId = 1,
                UserId = 1,
                Type = "Equipment",
                Manufacturer = "Caterpillar",
                Model = "CAT 320",
                ModelYear = "2020",
                BookValue = 55000
            };

            _mockAssetManager.Setup(x => x.UpdateAsset(asset)).ReturnsAsync(updatedAsset);

            // Act
            var result = await _controller.UpdateAsset(asset);

            // Assert
            var okResult = result.Result as OkObjectResult;
            okResult.Should().NotBeNull();
            okResult.StatusCode.Should().Be(200);
        }

        [Fact]
        public async Task UpdateAsset_WithInvalidAsset_ReturnsBadRequest()
        {
            // Arrange
            var asset = new AssetDTO
            {
                AssetId = 999,
                UserId = 1
            };

            _mockAssetManager.Setup(x => x.UpdateAsset(asset)).ReturnsAsync((AssetDTO)null);

            // Act
            var result = await _controller.UpdateAsset(asset);

            // Assert
            var badRequestResult = result.Result as BadRequestObjectResult;
            badRequestResult.Should().NotBeNull();
            badRequestResult.StatusCode.Should().Be(400);
        }
    }
}

