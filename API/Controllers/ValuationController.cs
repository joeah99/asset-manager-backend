using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using API.DTOs;
using API.Managers;
using Microsoft.Extensions.Logging;

namespace API.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ValuationController : ControllerBase
    {
        private readonly ILogger<ValuationController> _logger;
        private readonly ValuationManager _valuationManager;

        // Constructor injection of the AssetManager and ValuationManager
        public ValuationController(ILogger<ValuationController> logger, AssetManager assetManager, ValuationManager valuationManager)
        {
            _logger = logger;
            _valuationManager = valuationManager;
        }

        [HttpGet(Name = "GetAssetValuations")]
        public async Task<ActionResult<List<EquipmentValuationDTO>>> GetAssetValuations([FromQuery] int user_id)
        {
            var valuations = await _valuationManager.GetEquipmentValuations(user_id);

            if (valuations != null)
            {
                return Ok(valuations);
            }

            return NotFound("No equipment valuation data found.");
        }

        // GET: /Valuation/total-fmv?user_id=1
        [HttpGet("total-fmv", Name = "GetTotalFairMarketValue")]
        public async Task<ActionResult<List<MonthlyTotalFMVDTO>>> GetTotalFairMarketValue([FromQuery] int user_id)
        {
            var totalFMV = await _valuationManager.GetTotalFairMarketValue(user_id);

            if (totalFMV != null)
            {
                return Ok(totalFMV);
            }

            return NotFound("No total fair market value data found.");
        }

        [HttpGet("total-Asset-Value")]
        public async Task<ActionResult<TotalAssetValueDTO>> GetTotalAssetValue([FromQuery] int user_id)
        {
            var totalAssetValue = await _valuationManager.GetTotalAssetValue(user_id);

            if (totalAssetValue != null)
            {
                return Ok(totalAssetValue);
            }

            return NotFound("No total asset value data found.");
        }

        [HttpGet("adjusted-forced-liquidation")]
        public async Task<ActionResult<List<AdjustedForcedLiquidationDTO>>> GetAdjustedForcedLiquidation([FromQuery] int user_id)
        {
            var adjustedForcedLiquidation = await _valuationManager.GetAdjustedForcedLiquidationAsync(user_id);

            if (adjustedForcedLiquidation != null)
            {
                return Ok(adjustedForcedLiquidation);
            }

            return NotFound("No adjusted forced liquidation data found.");
        }
    }
}
