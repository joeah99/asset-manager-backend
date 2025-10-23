using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;
using API.DbContext;
using API.DTOs;
using API.Services;
using System.Globalization;

namespace API.Managers
{
  public class ValuationManager
  {
    private readonly ValuationDbContext _valuationDbContext;

    public ValuationManager(ValuationDbContext valuationDbContext)
    {
      _valuationDbContext = valuationDbContext;
    }

    public async Task<List<EquipmentValuationDTO>> GetEquipmentValuations(int user_id)
    {
      var valuationList = await _valuationDbContext.GetEquipmentValuationsAsync(user_id);
      return valuationList;
    }

    public async Task<List<MonthlyTotalFMVDTO>> GetTotalFairMarketValue(int user_id)
    {
      var totalFMVList = await GetEquipmentValuations(user_id);

      var monthlyTotalFMV = totalFMVList
          // Group by year and month so that duplicate month names in different years aren’t combined
          .GroupBy(ev => new { ev.ValuationDate.Year, ev.ValuationDate.Month })
          .Select(g => new
          {
            Year = g.Key.Year,
            MonthNumber = g.Key.Month,
            // Format the month name (if you prefer including the year, you could concatenate it)
            MonthName = new DateTime(g.Key.Year, g.Key.Month, 1).ToString("MMMM"),
            TotalFairMarketValue = g.Sum(ev => ev.AdjustedFairMarketValue),
            NumberOfAssets = g.Select(ev => ev.AssetId).Distinct().Count()
          })
          // Order descending to get the latest months first
          .OrderByDescending(x => new DateTime(x.Year, x.MonthNumber, 1))
          // Take only the latest 12 months
          .Take(12)
          // Re-order ascending (oldest-to-newest) if you prefer the output in chronological order
          .OrderBy(x => new DateTime(x.Year, x.MonthNumber, 1))
          .Select(x => new MonthlyTotalFMVDTO
          {
            Month = x.MonthName,
            TotalFairMarketValue = (double)x.TotalFairMarketValue,
            NumberOfAssets = x.NumberOfAssets
          })
          .ToList();

      return monthlyTotalFMV;
    }


    public async Task<TotalAssetValueDTO> GetTotalAssetValue(int user_id)
    {
      var totalFMVList = await GetTotalFairMarketValue(user_id);

      // Ensure we have data to compare
      if (totalFMVList == null || totalFMVList.Count == 0)
      {
        return null; // or throw an exception if appropriate
      }

      // Assumes totalFMVList is in chronological order (oldest first, latest last)
      var firstValue = totalFMVList.First().TotalFairMarketValue;
      var assetValue = totalFMVList.Last().TotalFairMarketValue;

      double percentChangeDouble = 0;
      if (firstValue != 0)
      {
        percentChangeDouble = ((assetValue - firstValue) / firstValue) * 100.0;
      }

      var totalAssetValue = new TotalAssetValueDTO
      {
        TotalAssetValue = assetValue,
        percentChangePastYear = (int)Math.Round(percentChangeDouble)
      };

      return totalAssetValue;
    }

    public async Task<List<AdjustedForcedLiquidationDTO>> GetAdjustedForcedLiquidationAsync(int user_id)
    {
      var valuationList = await _valuationDbContext.GetAdjustedForcedLiquidationAsync(user_id);

      var responseList = valuationList.Select(v => new AdjustedForcedLiquidationDTO
      {
        AssetId = v.AssetId,
        ValuationDate = v.ValuationDate.ToString("yyyy-MM-dd"),
        AdjustedForcedLiquidationValue = v.AdjustedForcedLiquidationValue
      }).OrderBy(dto => dto.AssetId).ToList();

      return responseList;
    }

  }
}