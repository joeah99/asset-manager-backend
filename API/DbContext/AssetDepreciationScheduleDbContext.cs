using MySql.Data.MySqlClient;
using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;

namespace API.DbContext
{
  public class AssetDepreciationScheduleDbContext
  {
    private readonly string _connectionString;

    public AssetDepreciationScheduleDbContext(string connectionString)
    {
      _connectionString = connectionString;
    }

    public async Task<AssetDepreciationScheduleDTO> CreateAssetDepreciationScheduleAsync(AssetDepreciationScheduleDTO assetDepreciationSchedule)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"INSERT INTO dbo.AssetDepreciationSchedule 
            (asset_id, depreciation_date, new_book_value, created_at)
            VALUES 
            (@asset_id, @depreciation_date, @new_book_value, GETDATE());
            SELECT SCOPE_IDENTITY()", conn);
        command.Parameters.AddWithValue("@asset_id", assetDepreciationSchedule.AssetId);
        command.Parameters.AddWithValue("@depreciation_date", assetDepreciationSchedule.DepreciationDate);
        command.Parameters.AddWithValue("@new_book_value", assetDepreciationSchedule.NewBookValue);

        var assetDepreciationScheduleId = (decimal)await command.ExecuteScalarAsync();
        assetDepreciationSchedule.AssetDepreciationScheduleId = (long)assetDepreciationScheduleId;
      }

      return assetDepreciationSchedule;
    }

    public async Task<List<AssetDepreciationScheduleDTO>> GetAssetDepreciationScheduleAsync(long assetDepreciationId)
    {
      var assetDepreciationScheduleList = new List<AssetDepreciationScheduleDTO>();

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"SELECT 
            asset_depreciation_schedule_id, asset_id, depreciation_date, new_book_value, created_at
            FROM dbo.AssetDepreciationSchedule
            WHERE asset_depreciation_id = @asset_depreciation_id", conn);
        command.Parameters.AddWithValue("@asset_depreciation_id", assetDepreciationId);

        using (var reader = await command.ExecuteReaderAsync())
        {
          while (await reader.ReadAsync())
          {
            var assetDepreciationSchedule = new AssetDepreciationScheduleDTO
            {
              AssetDepreciationScheduleId = reader.GetInt64(0),
              AssetId = reader.GetInt64(1),
              DepreciationDate = reader.GetString(2),
              NewBookValue = (float)reader.GetDecimal(3),
              CreatedAt = reader.GetDateTime(4)
            };
            assetDepreciationScheduleList.Add(assetDepreciationSchedule);
          }
        }
      }

      return assetDepreciationScheduleList;
    }

    public async Task<bool> DeleteAssetDepreciationScheduleAsync(long assetId)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"DELETE FROM dbo.AssetDepreciationSchedule
            WHERE asset_id = @asset_id", conn);
        command.Parameters.AddWithValue("@asset_id", assetId);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
      }
    }

    public async Task<List<DepreciationScheduleWithIdDTO>> GetAssetDepreciationAsync(long user_id)
        {
            var depreciationList = new List<DepreciationScheduleWithIdDTO>();

            using (var conn = new MySqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new MySqlCommand(
                    @"SELECT 
                  asset_id, 
                  depreciation_date,
                  new_book_value 
              FROM dbo.AssetDepreciationSchedule
              WHERE asset_id IN (SELECT asset_id FROM dbo.Asset WHERE user_id = @user_id)", conn);
                command.Parameters.AddWithValue("@user_id", user_id);

                using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        var dto = new DepreciationScheduleWithIdDTO
                        {
                            AssetId = reader.GetInt64(reader.GetOrdinal("asset_id")),
                            DepreciationDate = reader.GetString(reader.GetOrdinal("depreciation_date")),
                            NewBookValue = reader.IsDBNull(reader.GetOrdinal("new_book_value"))
                                ? 0
                                : (float)reader.GetDecimal(reader.GetOrdinal("new_book_value"))
                        };

                        depreciationList.Add(dto);
                    }
                }
            }

            return depreciationList;
        }
  }
  
}
