using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;
using API.DbContext;
using API.Services;

namespace API.Managers
{
    public class AssetManager
    {
        private readonly AssetDbContext _dbContext;
        private readonly ValuationDbContext _valuationDbContext;
        private readonly AssetDepreciationScheduleDbContext _assetDepreciationScheduleDbContext;
        private readonly AssetValuationService _assetValuationService;
        private readonly AssetDepreciationManager _assetDepreciationManager;

        public AssetManager(AssetDbContext dbContext, ValuationDbContext valuationDbContext, AssetValuationService assetValuationService, AssetDepreciationManager assetDepreciationManager, AssetDepreciationScheduleDbContext assetDepreciationScheduleDbContext)
        {
            _dbContext = dbContext;
            _valuationDbContext = valuationDbContext;
            _assetDepreciationScheduleDbContext = assetDepreciationScheduleDbContext;
            _assetValuationService = assetValuationService;
            _assetDepreciationManager = assetDepreciationManager;
        }

        public async Task<List<AssetDTO>> GetAssets(long user_id)
        {
            var assetList = await _dbContext.GetAssetsAsync(user_id);

            var valuationList = await _valuationDbContext.GetAdjustedForcedLiquidationAsync((int)user_id);

            var valuationsByAsset = valuationList
            .GroupBy(v => v.AssetId)
            .ToDictionary(
                g => g.Key,
                g => g.Select(v => new FairMarketValueDTO
                {
                    timeSet = v.ValuationDate,
                    value = (float)(v.AdjustedForcedLiquidationValue ?? 0)
                }).ToList()
            );
            var assetDepreciationList = await _assetDepreciationScheduleDbContext.GetAssetDepreciationAsync(user_id);
            var assetDepreciationByAsset = assetDepreciationList
            .GroupBy(d => d.AssetId)
            .ToDictionary(
                g => g.Key,
                g => g.Select(d => new AssetDepreciationDTO
                {
                    DepreciationDate = d.DepreciationDate,
                    NewBookValue = (float)d.NewBookValue
                }).ToList()
            );

            // Map assets to AssetDTO and append valuations
            var result = assetList.Select(asset => new AssetDTO
            {
                AssetId = asset.AssetId,
                UserId = asset.UserId,
                Type = asset.Type,
                BookValue = asset.BookValue,
                Manufacturer = asset.Manufacturer,
                Model = asset.Model,
                ModelYear = asset.ModelYear,
                Usage = asset.Usage,
                Condition = asset.Condition,
                Country = asset.Country,
                State = asset.State,
                CreateDate = asset.CreateDate,
                Deleted = asset.Deleted,
                DepreciationMethod = asset.DepreciationMethod,
                SalvageValue = asset.SalvageValue,
                UsefulLife = asset.UsefulLife,
                DepreciationRate = asset.DepreciationRate,
                TotalExpectedUnitsOfProduction = asset.TotalExpectedUnitsOfProduction,
                UnitsProducedInYear = asset.UnitsProducedInYear,
                UpdateDate = asset.UpdateDate,
                fairMarketValuesOverTime = valuationsByAsset.ContainsKey(asset.AssetId)
                    ? valuationsByAsset[asset.AssetId]
                    : new List<FairMarketValueDTO>(),
                assetDepreciationSchedule = assetDepreciationByAsset.ContainsKey(asset.AssetId)
                    ? assetDepreciationByAsset[asset.AssetId]
                    : new List<AssetDepreciationDTO>()
            }).ToList();

            return result;
        }

        public async Task<AssetDTO> CreateAsset(AssetDTO asset)
        {
            var existingAsset = await _dbContext.GetAssetAsync(asset.UserId, asset);

            if (existingAsset == null)
            {
                var newAsset = await _dbContext.CreateAssetAsync(asset);

                if (asset.Type == "Equipment")
                {
                    var equipmentValuation = await _assetValuationService.GetEquipmentValuationAsync(
                        asset.Manufacturer, asset.Model, asset.ModelYear, asset.Usage.ToString(), asset.Condition, asset.Country, asset.State);

                    await _valuationDbContext.InsertEquipmentValuationAsync(equipmentValuation, newAsset.AssetId);
                    newAsset.fairMarketValuesOverTime =
                    [
                        new FairMarketValueDTO
                        {
                            timeSet = DateTime.Now,
                            value = (float)(equipmentValuation.AdjustedForcedLiquidationValue ?? 0)
                        }
                    ];
                }
                else if (asset.Type == "Vehicle")
                {
                    var vehicleValuation = await _assetValuationService.GetVehicleValuationAsync(
                        asset.Manufacturer, asset.Model, asset.ModelYear, asset.Usage.ToString(), asset.Condition, asset.Country, asset.State);

                    await _valuationDbContext.InsertVehicleValuationAsync(vehicleValuation, newAsset.AssetId);
                    newAsset.fairMarketValuesOverTime =
                    [
                        new FairMarketValueDTO
                        {
                            timeSet = DateTime.Now,
                            value = (float)(vehicleValuation.AdjustedTradeIn ?? 0)
                        }
                    ];
                }

                newAsset = await _assetDepreciationManager.CreateAssetDepreciationSchedule(newAsset);
                return newAsset;
            }

            return null;
        }

        public async Task<List<EquipmentValuationDTO>> GetEquipmentValuations(int user_id)
        {
            var valuationList = await _valuationDbContext.GetEquipmentValuationsAsync(user_id);
            return valuationList;
        }

        public async Task DeleteAsset(AssetDTO asset)
        {
            try
            {
                await _dbContext.DeleteAssetAsync(asset);
            }
            catch (Exception e)
            {
                throw new Exception($"Error deleting asset {asset.AssetId}: {e.Message}");
            }
        }

        public async Task<AssetDTO> UpdateAsset(AssetDTO asset)
        {
            var updatedAsset = await _dbContext.UpdateAssetAsync(asset);
            if (asset.Type == "Equipment") {
                var equipmentValuation = await _assetValuationService.GetEquipmentValuationAsync(
                asset.Manufacturer, asset.Model, asset.ModelYear, asset.Usage.ToString(), asset.Condition, asset.Country, asset.State);

                await _valuationDbContext.InsertEquipmentValuationAsync(equipmentValuation, asset.AssetId);
                updatedAsset.fairMarketValuesOverTime =
                [
                    new FairMarketValueDTO
                    {
                        timeSet = DateTime.Now,
                        value = (float)(equipmentValuation.AdjustedForcedLiquidationValue ?? 0)
                    }
                ];
            } else if (asset.Type == "Vehicle") {
                var vehicleValuation = await _assetValuationService.GetVehicleValuationAsync(
                asset.Manufacturer, asset.Model, asset.ModelYear, asset.Usage.ToString(), asset.Condition, asset.Country, asset.State);

                await _valuationDbContext.InsertVehicleValuationAsync(vehicleValuation, asset.AssetId);
                updatedAsset.fairMarketValuesOverTime =
                [
                    new FairMarketValueDTO
                {
                        timeSet = DateTime.Now,
                        value = (float)(vehicleValuation.AdjustedTradeIn ?? 0)
                    }
                ];
            }

            updatedAsset = await _assetDepreciationManager.UpdateAssetDepreciationRecord(asset);
            return updatedAsset;
        }

    }
}
