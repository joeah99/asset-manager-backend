using Npgsql;
using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;

namespace API.DbContext
{
  public class ValuationDbContext
  {
    private readonly string _connectionString;

    public ValuationDbContext(string connectionString)
    {
      _connectionString = connectionString;
    }

    public async Task<List<EquipmentValuationDTO>> GetEquipmentValuationsAsync(int user_id)
    {
      var valuationsList = new List<EquipmentValuationDTO>();

      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          @"SELECT 
              log_id, asset_id, valuation_date, unadjusted_fair_market_value, unadjusted_orderly_liquidation_value, unadjusted_forced_liquidation_value,
              adjusted_fair_market_value, adjusted_orderly_liquidation_value, adjusted_forced_liquidation_value, salvage
            FROM ""EquipmentValuationLog""
            WHERE asset_id IN (
              SELECT asset_id FROM ""Asset"" WHERE user_id = @user_id
            );", conn);

        command.Parameters.AddWithValue("@user_id", user_id);

        using (var reader = await command.ExecuteReaderAsync())
        {
          while (await reader.ReadAsync())
          {
            var equipmentValuation = new EquipmentValuationDTO
            {
              LogId = reader.GetInt64(reader.GetOrdinal("log_id")),
              AssetId = reader.GetInt64(reader.GetOrdinal("asset_id")),
              ValuationDate = reader.GetDateTime(reader.GetOrdinal("valuation_date")),
              UnadjustedFairMarketValue = reader.IsDBNull(reader.GetOrdinal("unadjusted_fair_market_value")) ? 0 : reader.GetDouble(reader.GetOrdinal("unadjusted_fair_market_value")),
              UnadjustedOrderlyLiquidationValue = reader.IsDBNull(reader.GetOrdinal("unadjusted_orderly_liquidation_value")) ? 0 : reader.GetDouble(reader.GetOrdinal("unadjusted_orderly_liquidation_value")),
              UnadjustedForcedLiquidationValue = reader.IsDBNull(reader.GetOrdinal("unadjusted_forced_liquidation_value")) ? 0 : reader.GetDouble(reader.GetOrdinal("unadjusted_forced_liquidation_value")),
              AdjustedFairMarketValue = reader.IsDBNull(reader.GetOrdinal("adjusted_fair_market_value")) ? 0 : reader.GetDouble(reader.GetOrdinal("adjusted_fair_market_value")),
              AdjustedOrderlyLiquidationValue = reader.IsDBNull(reader.GetOrdinal("adjusted_orderly_liquidation_value")) ? 0 : reader.GetDouble(reader.GetOrdinal("adjusted_orderly_liquidation_value")),
              AdjustedForcedLiquidationValue = reader.IsDBNull(reader.GetOrdinal("adjusted_forced_liquidation_value")) ? 0 : reader.GetDouble(reader.GetOrdinal("adjusted_forced_liquidation_value")),
              Salvage = reader.IsDBNull(reader.GetOrdinal("salvage")) ? 0 : reader.GetDouble(reader.GetOrdinal("salvage"))
            };
            valuationsList.Add(equipmentValuation);
          }
        }

        return valuationsList;
      }
    }

    public async Task InsertEquipmentValuationAsync(EquipmentValuationDTO valuation, long assetId)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var insertCommand = new NpgsqlCommand(
          @"INSERT INTO ""EquipmentValuationLog"" 
            (asset_id, unadjusted_fair_market_value, 
             unadjusted_orderly_liquidation_value, unadjusted_forced_liquidation_value, 
             adjusted_fair_market_value, adjusted_orderly_liquidation_value, adjusted_forced_liquidation_value, 
             salvage, valuation_date)
            VALUES 
            (@asset_id, @unadjusted_fair_market_value, @unadjusted_orderly_liquidation_value, 
             @unadjusted_forced_liquidation_value, @adjusted_fair_market_value, @adjusted_orderly_liquidation_value, 
             @adjusted_forced_liquidation_value, @salvage, @valuation_date);", conn);

        insertCommand.Parameters.AddWithValue("@asset_id", assetId);
        insertCommand.Parameters.AddWithValue("@unadjusted_fair_market_value", valuation.UnadjustedFairMarketValue ?? 0);
        insertCommand.Parameters.AddWithValue("@unadjusted_orderly_liquidation_value", valuation.UnadjustedOrderlyLiquidationValue ?? 0);
        insertCommand.Parameters.AddWithValue("@unadjusted_forced_liquidation_value", valuation.UnadjustedForcedLiquidationValue ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_fair_market_value", valuation.AdjustedFairMarketValue ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_orderly_liquidation_value", valuation.AdjustedOrderlyLiquidationValue ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_forced_liquidation_value", valuation.AdjustedForcedLiquidationValue ?? 0);
        insertCommand.Parameters.AddWithValue("@salvage", valuation.Salvage ?? 0);
        insertCommand.Parameters.AddWithValue("@valuation_date", DateTime.UtcNow);

        await insertCommand.ExecuteNonQueryAsync();
      }
    }

    public async Task InsertVehicleValuationAsync(VehicleValuationDTO valuation, long assetId)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var insertCommand = new NpgsqlCommand(
          @"INSERT INTO ""VehicleValuationLog"" 
            (asset_id, unadjusted_low, unadjusted_high, 
             unadjusted_finance, unadjusted_retail, unadjusted_wholesale, unadjusted_trade_in, 
             adjusted_low, adjusted_high, adjusted_finance, adjusted_retail, adjusted_wholesale, adjusted_trade_in, 
             valuation_date)
            VALUES 
            (@asset_id, @unadjusted_low, @unadjusted_high, @unadjusted_finance, 
             @unadjusted_retail, @unadjusted_wholesale, @unadjusted_trade_in, 
             @adjusted_low, @adjusted_high, @adjusted_finance, @adjusted_retail, @adjusted_wholesale, 
             @adjusted_trade_in, @valuation_date);", conn);

        insertCommand.Parameters.AddWithValue("@asset_id", assetId);
        insertCommand.Parameters.AddWithValue("@unadjusted_low", valuation.UnadjustedLow ?? 0);
        insertCommand.Parameters.AddWithValue("@unadjusted_high", valuation.UnadjustedHigh ?? 0);
        insertCommand.Parameters.AddWithValue("@unadjusted_finance", valuation.UnadjustedFinance ?? 0);
        insertCommand.Parameters.AddWithValue("@unadjusted_retail", valuation.UnadjustedRetail ?? 0);
        insertCommand.Parameters.AddWithValue("@unadjusted_wholesale", valuation.UnadjustedWholesale ?? 0);
        insertCommand.Parameters.AddWithValue("@unadjusted_trade_in", valuation.UnadjustedTradeIn ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_low", valuation.AdjustedLow ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_high", valuation.AdjustedHigh ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_finance", valuation.AdjustedFinance ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_retail", valuation.AdjustedRetail ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_wholesale", valuation.AdjustedWholesale ?? 0);
        insertCommand.Parameters.AddWithValue("@adjusted_trade_in", valuation.AdjustedTradeIn ?? 0);
        insertCommand.Parameters.AddWithValue("@valuation_date", DateTime.UtcNow);

        await insertCommand.ExecuteNonQueryAsync();
      }
    }

    public async Task<List<AdjustedForcedLiquidation>> GetAdjustedForcedLiquidationAsync(int user_id)
    {
      var adjustedList = new List<AdjustedForcedLiquidation>();

      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          @"SELECT 
              asset_id, valuation_date, adjusted_forced_liquidation_value
            FROM ""EquipmentValuationLog""
            WHERE asset_id IN (
              SELECT asset_id FROM ""Asset"" WHERE user_id = @user_id
            );", conn);

        command.Parameters.AddWithValue("@user_id", user_id);

        using (var reader = await command.ExecuteReaderAsync())
        {
          while (await reader.ReadAsync())
          {
            var dto = new AdjustedForcedLiquidation
            {
              AssetId = reader.GetInt64(reader.GetOrdinal("asset_id")),
              ValuationDate = reader.GetDateTime(reader.GetOrdinal("valuation_date")),
              AdjustedForcedLiquidationValue = reader.IsDBNull(reader.GetOrdinal("adjusted_forced_liquidation_value"))
                ? 0
                : reader.GetDouble(reader.GetOrdinal("adjusted_forced_liquidation_value"))
            };

            adjustedList.Add(dto);
          }
        }
      }

      return adjustedList;
    }
  }
}
