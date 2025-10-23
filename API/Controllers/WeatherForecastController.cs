using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using API.DTOs;
using API.Managers;
using Microsoft.Extensions.Logging;

namespace API.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class EquipmentController : ControllerBase
    {
        private readonly ILogger<EquipmentController> _logger;
        private readonly EquipmentManager _equipmentManager;

        // Constructor injection of the EquipmentManager
        public EquipmentController(ILogger<EquipmentController> logger, EquipmentManager equipmentManager)
        {
            _logger = logger;
            _equipmentManager = equipmentManager;
        }

        [HttpGet(Name = "GetAssetInfo")]
        public async Task<ActionResult<List<AssetDTO>>> Get()
        {
            var equipment = await _equipmentManager.GetAssetInfo();

            if (equipment != null)
            {
                return Ok(equipment);
            }

            return NotFound("No equipment data found.");
        }
    }
}
