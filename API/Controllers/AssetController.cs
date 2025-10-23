using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using API.DTOs;
using API.Managers;
using Microsoft.Extensions.Logging;

namespace API.Controllers
{
    [ApiController]
    public class AssetController : ControllerBase
    {
        private readonly ILogger<AssetController> _logger;
        private readonly AssetManager _assetManager;

        // Constructor injection of the AssetManager
        public AssetController(ILogger<AssetController> logger, AssetManager assetManager)
        {
            _logger = logger;
            _assetManager = assetManager;
        }

        [HttpPost("GetAssets")]
        public async Task<ActionResult<List<AssetDTO>>> GetUserAssets([FromBody] long user_id) 
        {
          try
          {
            var assets = await _assetManager.GetAssets(user_id);

            if (assets != null)
            {
              return Ok(assets);
            }

            return NotFound("No equipment data found.");
          }
          catch (Exception e)
          {
            Console.WriteLine(e.Message);
            _logger.LogError(e, "An error occurred while getting assets for user {UserId}", user_id);
            return StatusCode(StatusCodes.Status500InternalServerError, new { message = e.Message });
          }
        }

        [HttpPost("CreateAsset")]
        public async Task<ActionResult<AssetDTO>> CreateAsset([FromBody] AssetDTO asset) 
        {

          try
          {
            var newAsset = await _assetManager.CreateAsset(asset);
            if (newAsset != null)
            {
              return Ok(new { asset = newAsset, message = "Asset created successfully." });
            }
            else
            {
              return BadRequest("Failed to create asset.");
            }
          }
          catch (Exception e)
          {
            Console.WriteLine(e.Message);
            _logger.LogError(e, "An error occurred while creating asset");
            return StatusCode(StatusCodes.Status500InternalServerError, new { message = e.Message });
          }
        }

        [HttpPut("DeleteAsset")]
        public async Task<ActionResult> DeleteAsset(AssetDTO asset) 
        {

          try {
            await _assetManager.DeleteAsset(asset);
          }
          catch (Exception e) {
            return StatusCode(StatusCodes.Status500InternalServerError, new { message = e.Message });
          }
          return Ok("The asset was deleted successfully.");
          
        }

        [HttpPut("UpdateAsset")]
        public async Task<ActionResult<AssetDTO>> UpdateAsset([FromBody] AssetDTO asset) 
        {
          try
          {
            var newAsset = await _assetManager.UpdateAsset(asset);
            if (newAsset != null)
            {
              return Ok(new { updatedAsset = newAsset, message = "Asset updated successfully." });
            }
            else
            {
              return BadRequest("Failed to update asset.");
            }
          }
          catch (Exception ex)
          {
            return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
          }
        }

    }
}
