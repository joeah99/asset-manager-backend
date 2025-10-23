using MySql.Data.MySqlClient;
using System.Collections.Generic;
using System.Numerics;
using System.Threading.Tasks;
using API.DTOs;

namespace API.DbContext
{
  public class DefaultDbContext
  {
    private readonly string _connectionString;

    public DefaultDbContext(string connectionString)
    {
      _connectionString = connectionString;
    }

    public async Task<List<AssetDTO>> GetAssetsAsync()
    {
      var assetList = new List<AssetDTO>();

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"SELECT TOP (1000) 
                        asset_id, user_id, asset_type, initial_book_value, manufacturer, model, model_year, usage, condition, country, state_us
                      FROM dbo.Asset", conn);

        using (var reader = await command.ExecuteReaderAsync())
        {
          while (await reader.ReadAsync())
          {
            var asset = new AssetDTO
            {
              AssetId = reader.GetInt64(0),
              UserId = reader.GetInt64(1),
              Type = reader.GetString(2),
              BookValue = reader.GetFloat(3),
              Manufacturer = reader.GetString(4),
              Model = reader.GetString(5),
              ModelYear = reader.GetString(6), // Read as string
              Usage = reader.GetInt32(7),
              Condition = reader.GetString(8),
              Country = reader.GetString(9),
            };
            assetList.Add(asset);
          }
        }
      }

      return assetList;
    }
  }
}

