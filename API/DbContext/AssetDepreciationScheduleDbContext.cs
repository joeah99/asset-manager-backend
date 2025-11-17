using Npgsql;
using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;
using System;

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
            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"INSERT INTO ""AssetDepreciationSchedule"" 
                        (asset_id, depreciation_date, new_book_value, created_at)
                      VALUES 
                        (@asset_id, @depreciation_date, @new_book_value, NOW())
                      RETURNING asset_depreciation_schedule_id;", conn);

                command.Parameters.AddWithValue("@asset_id", assetDepreciationSchedule.AssetId);
                command.Parameters.AddWithValue("@depreciation_date", assetDepreciationSchedule.DepreciationDate);

                // safe handling of possibly-null numeric field
                if (assetDepreciationSchedule.NewBookValue is float nbv)
                    command.Parameters.AddWithValue("@new_book_value", nbv);
                else
                    command.Parameters.AddWithValue("@new_book_value", DBNull.Value);

                var result = await command.ExecuteScalarAsync();
                assetDepreciationSchedule.AssetDepreciationScheduleId = (long)(result ?? 0L);
            }

            return assetDepreciationSchedule;
        }


        public async Task<List<AssetDepreciationScheduleDTO>> GetAssetDepreciationScheduleAsync(long assetDepreciationId)
        {
            var assetDepreciationScheduleList = new List<AssetDepreciationScheduleDTO>();

            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"SELECT 
                        asset_depreciation_schedule_id, 
                        asset_id, 
                        depreciation_date, 
                        new_book_value, 
                        created_at
                      FROM ""AssetDepreciationSchedule""
                      WHERE asset_depreciation_id = @asset_depreciation_id;", conn);

                command.Parameters.AddWithValue("@asset_depreciation_id", assetDepreciationId);

                await using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        var assetDepreciationSchedule = new AssetDepreciationScheduleDTO
                        {
                            AssetDepreciationScheduleId = reader.GetInt64(0),
                            AssetId = reader.GetInt64(1),
                            DepreciationDate = reader.GetString(2),
                            NewBookValue = reader.IsDBNull(3) ? 0 : (float)reader.GetDouble(3),
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
            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"DELETE FROM ""AssetDepreciationSchedule""
                      WHERE asset_id = @asset_id;", conn);

                command.Parameters.AddWithValue("@asset_id", assetId);

                var rowsAffected = await command.ExecuteNonQueryAsync();
                return rowsAffected > 0;
            }
        }

        public async Task<List<DepreciationScheduleWithIdDTO>> GetAssetDepreciationAsync(long user_id)
        {
            var depreciationList = new List<DepreciationScheduleWithIdDTO>();

            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"SELECT 
                        ads.asset_id, 
                        ads.depreciation_date,
                        ads.new_book_value 
                      FROM ""AssetDepreciationSchedule"" AS ads
                      WHERE ads.asset_id IN (
                          SELECT asset_id FROM ""Asset"" WHERE user_id = @user_id
                      );", conn);

                command.Parameters.AddWithValue("@user_id", user_id);

                await using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        var dto = new DepreciationScheduleWithIdDTO
                        {
                            AssetId = reader.GetInt64(reader.GetOrdinal("asset_id")),
                            DepreciationDate = reader.GetString(reader.GetOrdinal("depreciation_date")),
                            NewBookValue = reader.IsDBNull(reader.GetOrdinal("new_book_value"))
                                ? 0
                                : (float)reader.GetDouble(reader.GetOrdinal("new_book_value"))
                        };

                        depreciationList.Add(dto);
                    }
                }
            }

            return depreciationList;
        }
    }
}
