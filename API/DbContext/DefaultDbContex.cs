using Npgsql;
using System.Collections.Generic;
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

            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"SELECT 
                        asset_id, 
                        user_id, 
                        asset_type, 
                        initial_book_value, 
                        manufacturer, 
                        model, 
                        model_year, 
                        usage, 
                        condition, 
                        country, 
                        state_us
                      FROM ""Asset""
                      LIMIT 1000;", conn); // PostgreSQL uses LIMIT instead of TOP()

                await using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        var asset = new AssetDTO
                        {
                            AssetId = reader.GetInt64(reader.GetOrdinal("asset_id")),
                            UserId = reader.GetInt64(reader.GetOrdinal("user_id")),
                            Type = reader.GetString(reader.GetOrdinal("asset_type")),
                            BookValue = reader.IsDBNull(reader.GetOrdinal("initial_book_value"))
                                ? 0
                                : reader.GetFloat(reader.GetOrdinal("initial_book_value")),
                            Manufacturer = reader.IsDBNull(reader.GetOrdinal("manufacturer"))
                                ? string.Empty
                                : reader.GetString(reader.GetOrdinal("manufacturer")),
                            Model = reader.IsDBNull(reader.GetOrdinal("model"))
                                ? string.Empty
                                : reader.GetString(reader.GetOrdinal("model")),
                            ModelYear = reader.IsDBNull(reader.GetOrdinal("model_year"))
                                ? string.Empty
                                : reader.GetString(reader.GetOrdinal("model_year")),
                            Usage = reader.IsDBNull(reader.GetOrdinal("usage"))
                                ? 0
                                : reader.GetInt32(reader.GetOrdinal("usage")),
                            Condition = reader.IsDBNull(reader.GetOrdinal("condition"))
                                ? string.Empty
                                : reader.GetString(reader.GetOrdinal("condition")),
                            Country = reader.IsDBNull(reader.GetOrdinal("country"))
                                ? string.Empty
                                : reader.GetString(reader.GetOrdinal("country"))
                        };

                        assetList.Add(asset);
                    }
                }
            }

            return assetList;
        }
    }
}
