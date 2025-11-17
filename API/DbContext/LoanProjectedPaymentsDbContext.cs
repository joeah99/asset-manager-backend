using Npgsql;
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
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        // Use RETURNING for PostgreSQL instead of SCOPE_IDENTITY()
        var command = new NpgsqlCommand(
            @"INSERT INTO ""LoanProjectedPayments"" 
              (loan_id, loan_payment_date, new_remaining_value, created_at)
              VALUES 
              (@loan_id, @loan_payment_date, @new_remaining_value, @created_at)
              RETURNING loan_projected_payment_id;", conn);

        command.Parameters.AddWithValue("@loan_id", loanProjectedPayments.LoanId);
        command.Parameters.AddWithValue("@loan_payment_date", loanProjectedPayments.LoanPaymentDate);
        command.Parameters.AddWithValue("@new_remaining_value", loanProjectedPayments.NewRemainingValue);
        command.Parameters.AddWithValue("@created_at", DateTime.UtcNow);

        var loanProjectedPaymentId = (long)(await command.ExecuteScalarAsync())!;
        loanProjectedPayments.LoanProjectedPaymentId = loanProjectedPaymentId;
      }

      return loanProjectedPayments;
    }

    public async Task<List<LoanProjectedPaymentsDTO>> GetLoanProjectedPaymentsAsync(long loanId)
    {
      var loanProjectedPaymentsList = new List<LoanProjectedPaymentsDTO>();

      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
            @"SELECT 
                loan_projected_payment_id, loan_id, loan_payment_date, new_remaining_value, created_at
              FROM ""LoanProjectedPayments""
              WHERE loan_id = @loan_id;", conn);

        command.Parameters.AddWithValue("@loan_id", loanId);

        using (var reader = await command.ExecuteReaderAsync())
        {
          while (await reader.ReadAsync())
          {
            var loanProjectedPayments = new LoanProjectedPaymentsDTO
            {
              LoanProjectedPaymentId = reader.GetInt64(0),
              LoanId = reader.GetInt64(1),
              LoanPaymentDate = reader.GetDateTime(2).ToString("yyyy-MM-dd"),
              NewRemainingValue = reader.GetFloat(3),
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
      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new NpgsqlCommand(
            @"DELETE FROM ""LoanProjectedPayments"" 
              WHERE loan_id = @loan_id;", conn);

        command.Parameters.AddWithValue("@loan_id", loanId);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
      }
    }

    public async Task<List<LoanProjectedPaymentsDTO>> GetLoanProjectedPaymentsByUserIdAsync(long userId)
    {
      var loanProjectedPaymentsList = new List<LoanProjectedPaymentsDTO>();

      using (var conn = new NpgsqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        // Subquery syntax works the same, just adjust schema/table casing
        var command = new NpgsqlCommand(
            @"SELECT 
                p.loan_projected_payment_id, p.loan_id, p.loan_payment_date, p.new_remaining_value, p.created_at
              FROM ""LoanProjectedPayments"" p
              WHERE p.loan_id IN (
                SELECT l.loan_id FROM ""LoanInformation"" l WHERE l.user_id = @user_id
              );", conn);

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
              NewRemainingValue = reader.GetFloat(3),
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
