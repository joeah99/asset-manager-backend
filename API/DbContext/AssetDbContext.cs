using Npgsql; 
using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;

namespace API.DbContext
{
  public class AssetDbContext
  {
    private readonly string _connectionString;

    public AssetDbContext(string connectionString)
    {
      _connectionString = connectionString;
    }

    public async Task<List<AssetDTO>> GetAssetsAsync(long user_id)
    {
      var assetList = new List<AssetDTO>();

      await using var conn = new NpgsqlConnection(_connectionString);
      await conn.OpenAsync();

      var command = new NpgsqlCommand(
          @"SELECT 
              asset_id, user_id, asset_type, initial_book_value, manufacturer, model, model_year, usage, condition, country, state_us, deleted, 
              depreciation_method, salvage_value, useful_life, depreciation_rate, total_expected_units_production, 
              units_produced_in_year, created_at, updated_at
            FROM public.""Asset""
            WHERE user_id = @user_id AND deleted <> TRUE", conn);

      command.Parameters.AddWithValue("@user_id", user_id);

      await using var reader = await command.ExecuteReaderAsync();
      while (await reader.ReadAsync())
      {
        var asset = new AssetDTO
        {
          AssetId = reader.GetInt64(0),
          UserId = reader.GetInt64(1),
          Type = reader.GetString(2),
          BookValue = (float)reader.GetDouble(3),
          Manufacturer = reader.GetString(4),
          Model = reader.GetString(5),
          ModelYear = reader.GetString(6),
          Usage = reader.GetInt32(7),
          Condition = reader.GetString(8),
          Country = reader.GetString(9),
          State = reader.GetString(10),
          Deleted = reader.GetBoolean(11),
          DepreciationMethod = reader.GetString(12),
          SalvageValue = (float)reader.GetDecimal(13),
          UsefulLife = reader.GetInt32(14),
          DepreciationRate = (float)reader.GetDecimal(15),
          TotalExpectedUnitsOfProduction = reader.IsDBNull(16) ? 0 : reader.GetInt32(16),
          UnitsProducedInYear = reader.IsDBNull(17) ? 0 : reader.GetInt32(17),
          CreateDate = reader.GetDateTime(18).ToString("yyyy-MM-ddTHH:mm:ss"),
          UpdateDate = reader.GetDateTime(19).ToString("yyyy-MM-ddTHH:mm:ss")
        };
        assetList.Add(asset);
      }

      return assetList;
    }

    public async Task<AssetDTO?> GetAssetAsync(long userId, AssetDTO asset)
    {
      await using var conn = new NpgsqlConnection(_connectionString);
      await conn.OpenAsync();

      var command = new NpgsqlCommand(
        @"SELECT 
            asset_id, user_id, asset_type, manufacturer, model, model_year, usage, condition, country, state_us, created_at
          FROM public.""Asset""
          WHERE user_id = @user_id
            AND asset_type = @asset_type
            AND manufacturer = @manufacturer
            AND model = @model
            AND model_year = @model_year
            AND usage = @usage
            AND condition = @condition
            AND country = @country
            AND state_us = @state_us", conn);

      command.Parameters.AddWithValue("@user_id", userId);
      command.Parameters.AddWithValue("@asset_type", asset.Type);
      command.Parameters.AddWithValue("@manufacturer", asset.Manufacturer);
      command.Parameters.AddWithValue("@model", asset.Model);
      command.Parameters.AddWithValue("@model_year", asset.ModelYear);
      command.Parameters.AddWithValue("@usage", asset.Usage);
      command.Parameters.AddWithValue("@condition", asset.Condition);
      command.Parameters.AddWithValue("@country", asset.Country);
      command.Parameters.AddWithValue("@state_us", asset.State);

      await using var reader = await command.ExecuteReaderAsync();
      if (await reader.ReadAsync())
      {
        return new AssetDTO
        {
          AssetId = reader.GetInt64(0),
          UserId = reader.GetInt64(1),
          Type = reader.GetString(2),
          Manufacturer = reader.GetString(3),
          Model = reader.GetString(4),
          ModelYear = reader.GetString(5),
          Usage = reader.GetInt32(6),
          Condition = reader.GetString(7),
          Country = reader.GetString(8),
          State = reader.GetString(9),
          CreateDate = reader.GetDateTime(10).ToString("yyyy-MM-ddTHH:mm:ss")
        };
      }

      return null;
    }

    public async Task<List<AssetDTO>> GetAllAssetsAsync()
    {
      var assetList = new List<AssetDTO>();

      await using var conn = new NpgsqlConnection(_connectionString);
      await conn.OpenAsync();

      var command = new NpgsqlCommand(
          @"SELECT 
              asset_id, user_id, asset_type, initial_book_value, manufacturer, model, model_year, usage, condition, country, state_us, deleted, 
              depreciation_method, salvage_value, useful_life, depreciation_rate, total_expected_units_production, 
              units_produced_in_year, created_at, updated_at
            FROM public.""Asset""", conn);

      await using var reader = await command.ExecuteReaderAsync();
      while (await reader.ReadAsync())
      {
        var asset = new AssetDTO
        {
          AssetId = reader.GetInt64(0),
          UserId = reader.GetInt64(1),
          Type = reader.GetString(2),
          BookValue = (float)reader.GetDouble(3),
          Manufacturer = reader.GetString(4),
          Model = reader.GetString(5),
          ModelYear = reader.GetString(6),
          Usage = reader.GetInt32(7),
          Condition = reader.GetString(8),
          Country = reader.GetString(9),
          State = reader.GetString(10),
          Deleted = reader.GetBoolean(11),
          DepreciationMethod = reader.GetString(12),
          SalvageValue = (float)reader.GetDecimal(13),
          UsefulLife = reader.GetInt32(14),
          DepreciationRate = (float)reader.GetDecimal(15),
          TotalExpectedUnitsOfProduction = reader.IsDBNull(16) ? 0 : reader.GetInt32(16),
          UnitsProducedInYear = reader.IsDBNull(17) ? 0 : reader.GetInt32(17),
          CreateDate = reader.GetDateTime(18).ToString("yyyy-MM-ddTHH:mm:ss"),
          UpdateDate = reader.GetDateTime(19).ToString("yyyy-MM-ddTHH:mm:ss")
        };
        assetList.Add(asset);
      }

      return assetList;
    }

    public async Task<AssetDTO?> CreateAssetAsync(AssetDTO asset)
    {
      await using var conn = new NpgsqlConnection(_connectionString);
      await conn.OpenAsync();

      var insertCommand = new NpgsqlCommand(
          @"INSERT INTO public.""Asset"" 
            (user_id, asset_type, initial_book_value, manufacturer, model, model_year, usage, condition, country, state_us, depreciation_method,
             salvage_value, useful_life, depreciation_rate, total_expected_units_production, units_produced_in_year, created_at, updated_at)
           VALUES
            (@user_id, @asset_type, @initial_book_value, @manufacturer, @model, @model_year, @usage, @condition, @country, @state_us, @depreciation_method,
             @salvage_value, @useful_life, @depreciation_rate, @total_expected_units_production, @units_produced_in_year, @create_date, @update_date)
           RETURNING asset_id;", conn);

      insertCommand.Parameters.AddWithValue("@user_id", asset.UserId);
      insertCommand.Parameters.AddWithValue("@asset_type", asset.Type);
      insertCommand.Parameters.AddWithValue("@initial_book_value", asset.BookValue);
      insertCommand.Parameters.AddWithValue("@manufacturer", asset.Manufacturer);
      insertCommand.Parameters.AddWithValue("@model", asset.Model);
      insertCommand.Parameters.AddWithValue("@model_year", asset.ModelYear);
      insertCommand.Parameters.AddWithValue("@usage", asset.Usage);
      insertCommand.Parameters.AddWithValue("@condition", asset.Condition);
      insertCommand.Parameters.AddWithValue("@country", asset.Country);
      insertCommand.Parameters.AddWithValue("@state_us", asset.State);
      insertCommand.Parameters.AddWithValue("@depreciation_method", asset.DepreciationMethod);
      insertCommand.Parameters.AddWithValue("@salvage_value", asset.SalvageValue);
      insertCommand.Parameters.AddWithValue("@useful_life", asset.UsefulLife);
      insertCommand.Parameters.AddWithValue("@depreciation_rate", asset.DepreciationRate);
      insertCommand.Parameters.AddWithValue("@total_expected_units_production", asset.TotalExpectedUnitsOfProduction);
      insertCommand.Parameters.AddWithValue("@units_produced_in_year", asset.UnitsProducedInYear);
      insertCommand.Parameters.AddWithValue("@create_date", DateTime.Now);
      insertCommand.Parameters.AddWithValue("@update_date", DateTime.Now);

      var newAssetId = (long)await insertCommand.ExecuteScalarAsync();
      asset.AssetId = newAssetId;

      return asset;
    }

    public async Task DeleteAssetAsync(AssetDTO asset)
    {
      await using var conn = new NpgsqlConnection(_connectionString);
      await conn.OpenAsync();

      var deleteCommand = new NpgsqlCommand(
          @"UPDATE public.""Asset"" SET deleted = TRUE 
            WHERE user_id = @user_id AND asset_id = @asset_id", conn);

      deleteCommand.Parameters.AddWithValue("@user_id", asset.UserId);
      deleteCommand.Parameters.AddWithValue("@asset_id", asset.AssetId);

      await deleteCommand.ExecuteNonQueryAsync();
    }

    public async Task<AssetDTO> UpdateAssetAsync(AssetDTO asset)
    {
      await using var conn = new NpgsqlConnection(_connectionString);
      await conn.OpenAsync();

      var updateCommand = new NpgsqlCommand(
          @"UPDATE public.""Asset""
            SET asset_type = @asset_type,
                initial_book_value = @initial_book_value,
                manufacturer = @manufacturer,
                model = @model,
                model_year = @model_year,
                usage = @usage,
                condition = @condition,
                country = @country,
                state_us = @state_us,
                deleted = FALSE,
                depreciation_method = @depreciation_method,
                salvage_value = @salvage_value,
                useful_life = @useful_life,
                depreciation_rate = @depreciation_rate,
                total_expected_units_production = @total_expected_units_production,
                units_produced_in_year = @units_produced_in_year,
                updated_at = @update_date
            WHERE asset_id = @asset_id", conn);

      updateCommand.Parameters.AddWithValue("@asset_type", asset.Type);
      updateCommand.Parameters.AddWithValue("@initial_book_value", asset.BookValue);
      updateCommand.Parameters.AddWithValue("@manufacturer", asset.Manufacturer);
      updateCommand.Parameters.AddWithValue("@model", asset.Model);
      updateCommand.Parameters.AddWithValue("@model_year", asset.ModelYear);
      updateCommand.Parameters.AddWithValue("@usage", asset.Usage);
      updateCommand.Parameters.AddWithValue("@condition", asset.Condition);
      updateCommand.Parameters.AddWithValue("@country", asset.Country);
      updateCommand.Parameters.AddWithValue("@state_us", asset.State);
      updateCommand.Parameters.AddWithValue("@depreciation_method", asset.DepreciationMethod);
      updateCommand.Parameters.AddWithValue("@salvage_value", asset.SalvageValue);
      updateCommand.Parameters.AddWithValue("@useful_life", asset.UsefulLife);
      updateCommand.Parameters.AddWithValue("@depreciation_rate", asset.DepreciationRate ?? 0);
      updateCommand.Parameters.AddWithValue("@total_expected_units_production", asset.TotalExpectedUnitsOfProduction ?? 0);
      updateCommand.Parameters.AddWithValue("@units_produced_in_year", asset.UnitsProducedInYear ?? 0);
      updateCommand.Parameters.AddWithValue("@update_date", DateTime.Now);
      updateCommand.Parameters.AddWithValue("@asset_id", asset.AssetId);

      var rowsAffected = await updateCommand.ExecuteNonQueryAsync();
      if (rowsAffected == 0)
      {
        throw new Exception($"No rows were updated for asset {asset.AssetId}");
      }

      return asset;
    }
  }
}
