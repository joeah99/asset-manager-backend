using Npgsql;
using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;
using System;
using Isopoh.Cryptography.Argon2;

namespace API.DbContext
{
  public class AccountDbContext
  {
    private readonly string _connectionString;

    public AccountDbContext(string connectionString)
    {
      _connectionString = connectionString;
    }

    public async Task<bool> UserExists(string email)
    {
      bool responseValue = false;

      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          "SELECT CASE WHEN EXISTS (SELECT 1 FROM \"User\" WHERE email = @email) THEN TRUE ELSE FALSE END",
          conn);
        command.Parameters.AddWithValue("@email", email);

        var result = await command.ExecuteScalarAsync();
        responseValue = result != DBNull.Value && (bool)result;
      }

      return responseValue;
    }

    public async Task<bool> UsernameExists(string username)
    {
      bool responseValue = false;

      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          "SELECT CASE WHEN EXISTS (SELECT 1 FROM \"User\" WHERE username = @username) THEN TRUE ELSE FALSE END",
          conn);
        command.Parameters.AddWithValue("@username", username);

        var result = await command.ExecuteScalarAsync();
        responseValue = result != DBNull.Value && (bool)result;
      }

      return responseValue;
    }

    public async Task<bool> IsPasswordValid(LoginDto loginDto)
    {
      string hashedPassword = "";

      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();
        var command = new NpgsqlCommand(
          "SELECT hashed_password FROM \"User\" WHERE email = @email", conn);
        command.Parameters.AddWithValue("@email", loginDto.Email);

        var result = await command.ExecuteScalarAsync();
        if (result != null && result != DBNull.Value)
        {
          hashedPassword = (string)result;
        }
      }

      return Argon2.Verify(hashedPassword, loginDto.Password);
    }

    public async Task<AppUser?> GetUserByUsername(string email)
    {
      AppUser? user = null;

      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();
        var command = new NpgsqlCommand(
          "SELECT user_id, full_name, username, company, email, created_at FROM \"User\" WHERE email = @email",
          conn);
        command.Parameters.AddWithValue("@email", email);

        using (var reader = await command.ExecuteReaderAsync())
        {
          if (await reader.ReadAsync())
          {
            user = new AppUser
            {
              Id = reader.GetInt64(0),
              FullName = reader.GetString(1),
              Username = reader.GetString(2),
              Company = reader.IsDBNull(3) ? string.Empty : reader.GetString(3),
              Email = reader.GetString(4)
            };
          }
        }
      }

      return user;
    }

    public async Task<AppUser?> RegisterUser(AppUser user)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          "INSERT INTO \"User\" (full_name, username, hashed_password, email, created_at) " +
          "VALUES (@full_name, @username, @hashed_password, @email, @created_at) " +
          "RETURNING user_id;",
          conn);

        command.Parameters.AddWithValue("@full_name", user.FullName);
        command.Parameters.AddWithValue("@username", user.Username);
        command.Parameters.AddWithValue("@hashed_password", user.PasswordHash);
        command.Parameters.AddWithValue("@email", user.Email);
        command.Parameters.AddWithValue("@created_at", DateTime.UtcNow);

        var newUserId = await command.ExecuteScalarAsync();
        user.Id = Convert.ToInt64(newUserId);

        return user.Id > 0 ? user : null;
      }
    }

    public async Task<bool> DeleteUser(string email)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand("DELETE FROM \"User\" WHERE email = @email", conn);
        command.Parameters.AddWithValue("@email", email);

        int rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
      }
    }

    public async Task<bool> AddForgotPasswordToken(string token, string email)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          "INSERT INTO \"ForgotPasswordToken\" (token_hash, created_at, email) VALUES (@token, @createdAt, @email)",
          conn);
        command.Parameters.AddWithValue("@token", token);
        command.Parameters.AddWithValue("@createdAt", DateTime.UtcNow);
        command.Parameters.AddWithValue("@email", email);

        int rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
      }
    }

    public async Task<string?> VerifyPasswordResetToken(string resetTokenHash, string email)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          "SELECT token_hash, created_at FROM \"ForgotPasswordToken\" WHERE token_hash = @resetTokenHash AND email = @email",
          conn);
        command.Parameters.AddWithValue("@resetTokenHash", resetTokenHash);
        command.Parameters.AddWithValue("@email", email);

        string? tokenHash = null;
        DateTime? createdAt = null;

        using (var reader = await command.ExecuteReaderAsync())
        {
          if (await reader.ReadAsync())
          {
            tokenHash = reader.GetString(0);
            createdAt = reader.GetDateTime(1);
          }
        }

        if (createdAt == null || DateTime.UtcNow > createdAt.Value.AddMinutes(30) || tokenHash == null)
          return null;

        return tokenHash;
      }
    }

    public async Task<bool> ChangePassword(string password, string email)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          "UPDATE \"User\" SET hashed_password = @hashed_password WHERE email = @email",
          conn);
        command.Parameters.AddWithValue("@hashed_password", password);
        command.Parameters.AddWithValue("@email", email);

        int rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
      }
    }

    public async Task<bool> UpdateUser(AppUser user)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          "UPDATE \"User\" SET full_name = @full_name, company = @company, username = @username, email = @email WHERE user_id = @user_id",
          conn);

        command.Parameters.AddWithValue("@full_name", user.FullName);
        command.Parameters.AddWithValue("@company", user.Company);
        command.Parameters.AddWithValue("@username", user.Username);
        command.Parameters.AddWithValue("@email", user.Email);
        command.Parameters.AddWithValue("@user_id", user.Id);

        int rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
      }
    }

    public async Task<bool> SaveUserColumnPreferences(long userId, string columnPreferences)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var updateCommand = new NpgsqlCommand(
          "UPDATE \"UserPreferences\" SET column_preferences = @column_preferences, updated_at = @updated_at WHERE user_id = @user_id",
          conn);

        updateCommand.Parameters.AddWithValue("@user_id", userId);
        updateCommand.Parameters.AddWithValue("@column_preferences", columnPreferences);
        updateCommand.Parameters.AddWithValue("@updated_at", DateTime.UtcNow);

        int rowsAffected = await updateCommand.ExecuteNonQueryAsync();

        if (rowsAffected == 0)
        {
          var insertCommand = new NpgsqlCommand(
            "INSERT INTO \"UserPreferences\" (user_id, column_preferences, created_at, updated_at) " +
            "VALUES (@user_id, @column_preferences, @created_at, @updated_at)",
            conn);

          insertCommand.Parameters.AddWithValue("@user_id", userId);
          insertCommand.Parameters.AddWithValue("@column_preferences", columnPreferences);
          insertCommand.Parameters.AddWithValue("@created_at", DateTime.UtcNow);
          insertCommand.Parameters.AddWithValue("@updated_at", DateTime.UtcNow);

          rowsAffected = await insertCommand.ExecuteNonQueryAsync();
        }

        return rowsAffected > 0;
      }
    }

    public async Task<string?> GetUserColumnPreferences(long userId)
    {
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
          "SELECT column_preferences FROM \"UserPreferences\" WHERE user_id = @user_id",
          conn);
        command.Parameters.AddWithValue("@user_id", userId);

        var result = await command.ExecuteScalarAsync();
        return result != null && result != DBNull.Value ? (string)result : null;
      }
    }
  }
}
