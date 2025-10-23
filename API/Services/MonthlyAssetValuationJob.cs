using Quartz;
using API.DbContext;
using API.DTOs;
using API.Services;

namespace API.Services
{
    public class MonthlyAssetValuationJob : IJob
    {
        private readonly AssetDbContext _dbContext;
        private readonly ValuationDbContext _valuationDbContext;
        private readonly AssetValuationService _assetValuationService;

        public MonthlyAssetValuationJob(AssetDbContext dbContext, ValuationDbContext valuationDbContext, AssetValuationService assetValuationService)
        {
            _dbContext = dbContext;
            _valuationDbContext = valuationDbContext;
            _assetValuationService = assetValuationService;
        }

        public async Task<List<AssetDTO>> GetAllAssetsAsync()
        {
            var assetList = await _dbContext.GetAllAssetsAsync();
            return assetList;
        }

        public async Task CreateAssetValuationAsync(AssetDTO asset) {
            if(asset.Type == "Equipment") {
                var equipmentValuation = await _assetValuationService.GetEquipmentValuationAsync(
                    asset.Manufacturer, asset.Model, asset.ModelYear, asset.Usage.ToString(), asset.Condition, asset.Country, asset.State);

                await _valuationDbContext.InsertEquipmentValuationAsync(equipmentValuation, asset.AssetId);
            } else if(asset.Type == "Vehicle") {
                var vehicleValuation = await _assetValuationService.GetVehicleValuationAsync(
                    asset.Manufacturer, asset.Model, asset.ModelYear, asset.Usage.ToString(), asset.Condition, asset.Country, asset.State);

                await _valuationDbContext.InsertVehicleValuationAsync(vehicleValuation, asset.AssetId);
            }
        }

        public async Task Execute(IJobExecutionContext context) {
            var assets = await GetAllAssetsAsync();
            try { 
                foreach (var asset in assets) {
                    await CreateAssetValuationAsync(asset);
                }
            }
            catch (AggregateException ae){
                Console.WriteLine(ae.Message);
            }
        }
    }
}