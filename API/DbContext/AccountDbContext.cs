using MySql.Data.MySqlClient;
using System.Collections.Generic;
using System.Numerics;
using System.Threading.Tasks;
using API.DTOs;
using System.Text;
using System.ComponentModel;
using Azure;
using System.Text.Json;

using MySql.Data.MySqlClient;
using System.Threading.Tasks;
using System.ComponentModel.Design;
using Isopoh.Cryptography.Argon2;
using System.Data;

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
      var responseValue = false;

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand("SELECT CASE WHEN EXISTS (SELECT 1 FROM dbo.[User] WHERE email = @email) THEN 1 ELSE 0 END", conn);
        command.Parameters.AddWithValue("@email", email);

        using (var reader = await command.ExecuteReaderAsync())
        {
          if (await reader.ReadAsync())
          {
            responseValue = reader.GetInt32(0) == 1;
            // Reads the integer (0 or 1) and converts to boolean
            // 1 = true
            // 0 = false
          }
        }
      }
      return responseValue;
    }

    public async Task<bool> UsernameExists(string username)
    {
      var responseValue = false;

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand("SELECT CASE WHEN EXISTS (SELECT 1 FROM dbo.[User] WHERE username = @username) THEN 1 ELSE 0 END", conn);
        command.Parameters.AddWithValue("@username", username);

        using (var reader = await command.ExecuteReaderAsync())
        {
          if (await reader.ReadAsync())
          {
            responseValue = reader.GetInt32(0) == 1;
          }
        }
      }
      return responseValue;
    }

    public async Task<bool> IsPasswordValid(LoginDto loginDto)
    {

      var hashedPassword = "";

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();
        var command = new MySqlCommand("SELECT hashed_password FROM dbo.[User] WHERE email = @email", conn);
        command.Parameters.AddWithValue("@email", loginDto.Email);

        using (var reader = await command.ExecuteReaderAsync())
        {
          if (await reader.ReadAsync())
          {
            hashedPassword = reader.GetString(0);
          }
        }
      }

      if (Argon2.Verify(hashedPassword, loginDto.Password))
      {
        return true;
      }
      else return false;
    }

    public async Task<AppUser?> GetUserByUsername(string email)
    {
      AppUser? user = null;

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();
        var command = new MySqlCommand("SELECT user_id, full_name, username, company, email, created_at FROM dbo.[User] WHERE email = @email", conn);
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
              Email = reader.GetString(4),
            };
          }
        }
      }

      return user;
    }


    public async Task<AppUser?> RegisterUser(AppUser user)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            "INSERT INTO [User] (full_name, username, hashed_password, email, created_at) " +
            "VALUES (@full_name, @username, @hashed_password, @email, @created_at); " +
            "SELECT SCOPE_IDENTITY(); ", conn);

        // Add parameters to prevent SQL injection
        command.Parameters.AddWithValue("@full_name", user.FullName);
        command.Parameters.AddWithValue("@username", user.Username);
        command.Parameters.AddWithValue("@hashed_password", user.PasswordHash);
        command.Parameters.AddWithValue("@email", user.Email);
        command.Parameters.AddWithValue("@created_at", DateTime.Now);

        var newUserId = (decimal)await command.ExecuteScalarAsync();
        user.Id = (long)newUserId;

        // Return true if the insert was successful (1 or more rows affected)
        if (newUserId > 0)
        {
          return user;
        }
        else return null;
      }
    }

    public async Task<bool> DeleteUser(string email)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand("DELETE FROM dbo.[User] WHERE email = @email", conn);
        command.Parameters.AddWithValue("@email", email);

        int rowsAffected = await command.ExecuteNonQueryAsync();

        return rowsAffected > 0;
      }
    }

    public async Task<bool> AddForgotPasswordToken(string token, string email)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand("INSERT INTO dbo.ForgotPasswordToken (token_hash, created_at, email) VALUES (@token, @createdAt, @email)", conn);
        command.Parameters.AddWithValue("@token", token);
        command.Parameters.AddWithValue("@createdAt", DateTime.Now);
        command.Parameters.AddWithValue("@email", email);

        int rowsAffected = await command.ExecuteNonQueryAsync();

        return rowsAffected > 0;
      }
    }

    public async Task<string> VerifyPasswordResetToken(string resetTokenHash, string email)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand("SELECT token_hash, created_at FROM dbo.ForgotPasswordToken WHERE token_hash = @resetTokenHash AND email = @email", conn);
        command.Parameters.AddWithValue("@resetTokenHash", resetTokenHash);
        command.Parameters.AddWithValue("@email", email);

        string tokenHash = null;
        DateTime? createdAt = null;

        using (var reader = await command.ExecuteReaderAsync())
        {
          if (await reader.ReadAsync())
          {
            tokenHash = reader.GetString(0);
            createdAt = reader.GetDateTime(1);
          }
        }

        if (createdAt == null || DateTime.Now > createdAt.Value.AddMinutes(30) || tokenHash == null)
        {
          return null;
        }

        return tokenHash;
      }
    }

    public async Task<bool> ChangePassword(string password, string email)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand("UPDATE [User] SET hashed_password = @hashed_password WHERE email = @email", conn);
        command.Parameters.AddWithValue("@hashed_password", password);
        command.Parameters.AddWithValue("@email", email);

        int rowsAffected = await command.ExecuteNonQueryAsync();

        return rowsAffected > 0;
      }
    }

    public async Task<bool> UpdateUser(AppUser user)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            "UPDATE [User] SET full_name = @full_name, company = @company, username = @username, email = @email WHERE user_id = @user_id", conn);

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
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        // First try to update existing preferences
        var updateCommand = new MySqlCommand(
            "UPDATE [UserPreferences] SET column_preferences = @column_preferences, updated_at = @updated_at " +
            "WHERE user_id = @user_id", conn);

        updateCommand.Parameters.AddWithValue("@user_id", userId);
        updateCommand.Parameters.AddWithValue("@column_preferences", columnPreferences);
        updateCommand.Parameters.AddWithValue("@updated_at", DateTime.Now);

        int rowsAffected = await updateCommand.ExecuteNonQueryAsync();

        if (rowsAffected == 0)
        {
          // If no rows were updated, insert new preferences
          var insertCommand = new MySqlCommand(
              "INSERT INTO [UserPreferences] (user_id, column_preferences, created_at, updated_at) " +
              "VALUES (@user_id, @column_preferences, @created_at, @updated_at)", conn);

          insertCommand.Parameters.AddWithValue("@user_id", userId);
          insertCommand.Parameters.AddWithValue("@column_preferences", columnPreferences);
          insertCommand.Parameters.AddWithValue("@created_at", DateTime.Now);
          insertCommand.Parameters.AddWithValue("@updated_at", DateTime.Now);

          rowsAffected = await insertCommand.ExecuteNonQueryAsync();
        }

        return rowsAffected > 0;
      }
    }

    public async Task<string?> GetUserColumnPreferences(long userId)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            "SELECT column_preferences FROM [UserPreferences] WHERE user_id = @user_id", conn);
        command.Parameters.AddWithValue("@user_id", userId);

        using (var reader = await command.ExecuteReaderAsync())
        {
          if (await reader.ReadAsync())
          {
            return reader.GetString(0);
          }
        }
      }
      return null;
    }
  }
}
