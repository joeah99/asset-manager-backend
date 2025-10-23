using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;
using API.DbContext;
using API.Services;
using System.Security.Cryptography;

namespace API.Managers
{
    public class AssetDepreciationManager
    {
        private readonly AssetDepreciationScheduleDbContext _scheduleDbContext;
        private readonly AssetDepreciationService _assetDepreciationService;

        public AssetDepreciationManager(AssetDepreciationScheduleDbContext scheduleDbContext, AssetDepreciationService assetDepreciationService)
        {
            _scheduleDbContext = scheduleDbContext;
            _assetDepreciationService = assetDepreciationService;
        }

        public async Task<AssetDTO> CreateAssetDepreciationSchedule(AssetDTO assetDepreciation)
        {
            List<AssetDepreciationDTO> endOfMonthValues = new List<AssetDepreciationDTO>();
            switch (assetDepreciation.DepreciationMethod)
            {
                case "StraightLine":
                    assetDepreciation.DepreciationRate = 0;
                    assetDepreciation.UnitsProducedInYear = 0;
                    assetDepreciation.TotalExpectedUnitsOfProduction = 0;
                    try
                    {
                        if (assetDepreciation.UsefulLife.HasValue)
                        {
                            endOfMonthValues = _assetDepreciationService.StraightLineDepreciation((double)assetDepreciation.BookValue, (double)assetDepreciation.SalvageValue, assetDepreciation.UsefulLife.Value);
                        }
                        else
                        {
                            throw new ArgumentException("Useful life is required for straight-line depreciation.");
                        }
                    }
                    catch (Exception ex)
                    {
                        throw new Exception(ex.Message);
                    }
                    break;
                case "DecliningBalance":
                    assetDepreciation.TotalExpectedUnitsOfProduction = 0;
                    assetDepreciation.UnitsProducedInYear = 0;
                    try
                    {
                        if (assetDepreciation.UsefulLife.HasValue && assetDepreciation.DepreciationRate.HasValue)
                        {
                            endOfMonthValues = _assetDepreciationService.DecliningBalanceDepreciation((double)assetDepreciation.BookValue, (double)assetDepreciation.SalvageValue, assetDepreciation.UsefulLife.Value, assetDepreciation.DepreciationRate.Value);
                        }
                        else
                        {
                            throw new ArgumentException("Useful life and depreciation rate are required for declining balance depreciation.");
                        }
                    }
                    catch (Exception ex)
                    {
                        throw new Exception(ex.Message);
                    }
                    break;
                case "DoubleDecliningBalance":
                    assetDepreciation.DepreciationRate = 0;
                    assetDepreciation.UnitsProducedInYear = 0;
                    assetDepreciation.TotalExpectedUnitsOfProduction = 0;
                    try
                    {
                        if (assetDepreciation.UsefulLife.HasValue)
                        {
                            endOfMonthValues = _assetDepreciationService.DoubleDecliningBalanceDepreciation((double)assetDepreciation.BookValue, (double)assetDepreciation.SalvageValue, assetDepreciation.UsefulLife.Value);
                        }
                        else
                        {
                            throw new ArgumentException("Useful life is required for double declining balance depreciation.");
                        }
                    }
                    catch (Exception ex)
                    {
                        throw new Exception(ex.Message);
                    }
                    break;
                case "UnitsOfProduction":
                    assetDepreciation.DepreciationRate = 0;
                    assetDepreciation.UsefulLife = 0;
                    try
                    {
                        if (assetDepreciation.TotalExpectedUnitsOfProduction.HasValue && assetDepreciation.UnitsProducedInYear.HasValue)
                        {
                            endOfMonthValues = _assetDepreciationService.UnitsOfProductionDepreciation((double)assetDepreciation.BookValue, (double)assetDepreciation.SalvageValue, assetDepreciation.TotalExpectedUnitsOfProduction.Value, assetDepreciation.UnitsProducedInYear.Value);
                        }
                        else
                        {
                            throw new ArgumentException("Total expected units of production and units produced in year are required for units of production depreciation.");
                        }
                    }
                    catch (Exception ex)
                    {
                        throw new Exception(ex.Message);
                    }

                    break;
                default:
                    throw new Exception("Invalid depreciation method.");
            }

            if (endOfMonthValues.Count > 0)
            {
                if (assetDepreciation.AssetId > 0)
                {
                    foreach (var assetDepreciationDTO in endOfMonthValues)
                    {
                        var assetDepreciationSchedule = new AssetDepreciationScheduleDTO
                        {
                            AssetDepreciationScheduleId = 0,
                            AssetId = assetDepreciation.AssetId,
                            DepreciationDate = assetDepreciationDTO.DepreciationDate,
                            NewBookValue = (float)assetDepreciationDTO.NewBookValue,
                            CreatedAt = DateTime.Now
                        };
                        await _scheduleDbContext.CreateAssetDepreciationScheduleAsync(assetDepreciationSchedule);
                    }
                }
                else
                {
                    throw new Exception("Failed to create asset depreciation.");
                }
                assetDepreciation.assetDepreciationSchedule = endOfMonthValues;
                return assetDepreciation;
            }
            else
            {
                throw new Exception("Failed to calculate depreciation schedule.");
            }
        }

        public async Task<List<AssetDepreciationScheduleDTO>> GetAssetDepreciationSchedule(long assetId) {
            var assetDepreciationSchedule = await _scheduleDbContext.GetAssetDepreciationScheduleAsync(assetId);
            if (assetDepreciationSchedule != null)
            {
                return assetDepreciationSchedule;
            }
            else
            {
                throw new Exception("Asset depreciation schedule not found.");
            }
        }

        public async Task<AssetDTO> UpdateAssetDepreciationRecord(AssetDTO assetDepreciation)
        {
            if (assetDepreciation.AssetId > 0)
            {
                List<AssetDepreciationDTO> endOfMonthValues = new List<AssetDepreciationDTO>();
                switch (assetDepreciation.DepreciationMethod)
                {
                    case "StraightLine":
                        assetDepreciation.DepreciationRate = 0;
                        assetDepreciation.UnitsProducedInYear = 0;
                        assetDepreciation.TotalExpectedUnitsOfProduction = 0;
                        try
                        {
                            if (assetDepreciation.UsefulLife.HasValue)
                            {
                                endOfMonthValues = _assetDepreciationService.StraightLineDepreciation((double)assetDepreciation.BookValue, (double)assetDepreciation.SalvageValue, assetDepreciation.UsefulLife.Value);
                            }
                            else
                            {
                                throw new ArgumentException("Useful life is required for straight-line depreciation.");
                            }
                        }
                        catch (Exception ex)
                        {
                            throw new Exception(ex.Message);
                        }
                        break;
                    case "DecliningBalance":
                        assetDepreciation.TotalExpectedUnitsOfProduction = 0;
                        assetDepreciation.UnitsProducedInYear = 0;
                        try
                        {
                            if (assetDepreciation.UsefulLife.HasValue && assetDepreciation.DepreciationRate.HasValue)
                            {
                                endOfMonthValues = _assetDepreciationService.DecliningBalanceDepreciation((double)assetDepreciation.BookValue, (double)assetDepreciation.SalvageValue, assetDepreciation.UsefulLife.Value, assetDepreciation.DepreciationRate.Value);
                            }
                            else
                            {
                                throw new ArgumentException("Useful life and depreciation rate are required for declining balance depreciation.");
                            }
                        }
                        catch (Exception ex)
                        {
                            throw new Exception(ex.Message);
                        }
                        break;
                    case "DoubleDecliningBalance":
                        assetDepreciation.DepreciationRate = 0;
                        assetDepreciation.UnitsProducedInYear = 0;
                        assetDepreciation.TotalExpectedUnitsOfProduction = 0;
                        try
                        {
                            if (assetDepreciation.UsefulLife.HasValue)
                            {
                                endOfMonthValues = _assetDepreciationService.DoubleDecliningBalanceDepreciation((double)assetDepreciation.BookValue, (double)assetDepreciation.SalvageValue, assetDepreciation.UsefulLife.Value);
                            }
                            else
                            {
                                throw new ArgumentException("Useful life is required for double declining balance depreciation.");
                            }
                        }
                        catch (Exception ex)
                        {
                            throw new Exception(ex.Message);
                        }
                        break;
                    case "UnitsOfProduction":
                        assetDepreciation.DepreciationRate = 0;
                        assetDepreciation.UsefulLife = 0;
                        try
                        {
                            if (assetDepreciation.TotalExpectedUnitsOfProduction.HasValue && assetDepreciation.UnitsProducedInYear.HasValue)
                            {
                                endOfMonthValues = _assetDepreciationService.UnitsOfProductionDepreciation((double)assetDepreciation.BookValue, (double)assetDepreciation.SalvageValue, assetDepreciation.TotalExpectedUnitsOfProduction.Value, assetDepreciation.UnitsProducedInYear.Value);
                            }
                            else
                            {
                                throw new ArgumentException("Total expected units of production and units produced in year are required for units of production depreciation.");
                            }
                        }
                        catch (Exception ex)
                        {
                            throw new Exception(ex.Message);
                        }

                        break;
                    default:
                        throw new Exception("Invalid depreciation method.");
                }

                if (endOfMonthValues.Count > 0)
                {
                    await _scheduleDbContext.DeleteAssetDepreciationScheduleAsync(assetDepreciation.AssetId);
                    
                        foreach (var assetDepreciationDTO in endOfMonthValues)
                        {
                            var assetDepreciationSchedule = new AssetDepreciationScheduleDTO
                            {
                                AssetDepreciationScheduleId = 0,
                                AssetId = assetDepreciation.AssetId,
                                DepreciationDate = assetDepreciationDTO.DepreciationDate,
                                NewBookValue = (float)assetDepreciationDTO.NewBookValue,
                                CreatedAt = DateTime.Now
                            };
                            await _scheduleDbContext.CreateAssetDepreciationScheduleAsync(assetDepreciationSchedule);
                        }
                    assetDepreciation.assetDepreciationSchedule = endOfMonthValues;
                    return assetDepreciation;
                }
                else
                {
                    throw new Exception("Failed to calculate depreciation schedule.");
                }
            }
            else
            {
                throw new Exception("Asset depreciation record not found.");
            }
        }

    }
}
