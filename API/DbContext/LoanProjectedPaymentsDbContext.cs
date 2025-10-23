using MySql.Data.MySqlClient;
using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;

namespace API.DbContext
{
  public class LoanProjectedPaymentsDbContext
  {
    private readonly string _connectionString;

    public LoanProjectedPaymentsDbContext(string connectionString)
    {
      _connectionString = connectionString;
    }

    public async Task<LoanProjectedPaymentsDTO> CreateLoanProjectedPaymentsAsync(LoanProjectedPaymentsDTO loanProjectedPayments)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"INSERT INTO dbo.LoanProjectedPayments 
            (loan_id, loan_payment_date, new_remaining_value, created_at)
            VALUES 
            (@loan_id, @loan_payment_date, @new_remaining_value, @created_at);
            SELECT SCOPE_IDENTITY()", conn);
        command.Parameters.AddWithValue("@loan_id", loanProjectedPayments.LoanId);
        command.Parameters.AddWithValue("@loan_payment_date", loanProjectedPayments.LoanPaymentDate);
        command.Parameters.AddWithValue("@new_remaining_value", loanProjectedPayments.NewRemainingValue);
        command.Parameters.AddWithValue("@created_at", DateTime.Now);

        var loanProjectedPaymentId = (decimal)await command.ExecuteScalarAsync();
        loanProjectedPayments.LoanProjectedPaymentId = (long)loanProjectedPaymentId;
      }

      return loanProjectedPayments;
    }

    public async Task<List<LoanProjectedPaymentsDTO>> GetLoanProjectedPaymentsAsync(long loanId)
    {
      var loanProjectedPaymentsList = new List<LoanProjectedPaymentsDTO>();

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"SELECT 
            loan_projected_payment_id, loan_id, loan_payment_date, new_remaining_value, created_at
            FROM dbo.LoanProjectedPayments
            WHERE loan_id = @loan_id", conn);
        command.Parameters.AddWithValue("@loan_id", loanId);

        using (var reader = await command.ExecuteReaderAsync())
        {
          while (await reader.ReadAsync())
          {
            var loanProjectedPayments = new LoanProjectedPaymentsDTO
            {
              LoanProjectedPaymentId = reader.GetInt64(0),
              LoanId = reader.GetInt64(1),
              LoanPaymentDate = reader.GetString(2),
              NewRemainingValue = (float)reader.GetDecimal(3),
              CreatedAt = reader.GetDateTime(4)
            };
            loanProjectedPaymentsList.Add(loanProjectedPayments);
          }
        }
      }

      return loanProjectedPaymentsList;
    }

    public async Task<bool> DeleteLoanProjectedPaymentsAsync(long loanId)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"DELETE FROM dbo.LoanProjectedPayments 
            WHERE loan_id = @loan_id", conn);
        command.Parameters.AddWithValue("@loan_id", loanId);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
      }
    }

    public async Task<List<LoanProjectedPaymentsDTO>> GetLoanProjectedPaymentsByUserIdAsync(long userId)
    {
      var loanProjectedPaymentsList = new List<LoanProjectedPaymentsDTO>();

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"SELECT
            loan_projected_payment_id, loan_id, loan_payment_date, new_remaining_value, created_at
            FROM dbo.LoanProjectedPayments
            WHERE loan_id IN (SELECT loan_id FROM dbo.LoanInformation WHERE user_id = @user_id)", conn);
        command.Parameters.AddWithValue("@user_id", userId);

        using (var reader = await command.ExecuteReaderAsync())
        {
          while (await reader.ReadAsync())
          {
            var loanProjectedPayments = new LoanProjectedPaymentsDTO
            {
              LoanProjectedPaymentId = reader.GetInt64(0),
              LoanId = reader.GetInt64(1),
              LoanPaymentDate = reader.GetDateTime(2).ToString("yyyy-MM-dd"),
              NewRemainingValue = (float)reader.GetDecimal(3),
              CreatedAt = reader.GetDateTime(4)
            };
            loanProjectedPaymentsList.Add(loanProjectedPayments);
          }
        }
      }
      return loanProjectedPaymentsList;
    }
  }
  
}
