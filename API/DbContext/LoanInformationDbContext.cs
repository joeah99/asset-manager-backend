using MySql.Data.MySqlClient;
using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;

namespace API.DbContext
{
  public class LoanInformationDbContext
  {
    private readonly string _connectionString;

    public LoanInformationDbContext(string connectionString)
    {
      _connectionString = connectionString;
    }
    
    public async Task<List<LoanInformationDTO>> GetLoansAsync(long user_id)
    {
      var loanList = new List<LoanInformationDTO>();

      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
            @"SELECT 
                        loan_id, asset_id, user_id, lender_name, loan_amount, interest_rate, loan_term_years, remaining_balance, 
                        monthly_payment, payment_frequency, loan_status, last_payment_date, last_payment_amount, next_payment_date, 
                        loan_start_date, loan_end_date, created_at, updated_at
                      FROM dbo.LoanInformation
                      WHERE user_id = @user_id", conn);
        command.Parameters.AddWithValue("@user_id", user_id);

        using (var reader = await command.ExecuteReaderAsync())
        {
          while (await reader.ReadAsync())
          {
            var loan = new LoanInformationDTO
            {
              LoanId = reader.GetInt64(0),
              AssetId = reader.GetInt64(1),
              UserId = reader.GetInt64(2),
              LenderName = reader.GetString(3),
              LoanAmount = (float)reader.GetDecimal(4),
              InterestRate = (float)reader.GetDecimal(5),
              LoanTermYears = reader.GetInt32(6),
              RemainingBalance = (float)reader.GetDecimal(7),
              MonthlyPayment = (float)reader.GetDecimal(8),
              PaymentFrequency = reader.GetString(9),
              Status = reader.GetString(10),
              LastPaymentDate = reader.GetString(11),
              LastPaymentAmount = (float)reader.GetDecimal(12),
              NextPaymentDate = reader.GetString(13),
              LoanStartDate = reader.GetString(14),
              LoanEndDate = reader.GetString(15),
              LoanCreation = reader.GetDateTime(16),
              LoanUpdate = reader.GetDateTime(17)
            };
            loanList.Add(loan);
          }
        }
      }

      return loanList;
    }

    public async Task<LoanInformationDTO?> CreateLoanRecordAsync(LoanInformationDTO loan)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
          @"INSERT INTO dbo.LoanInformation 
            (asset_id, user_id, lender_name, loan_amount, interest_rate, loan_term_years, remaining_balance, 
            monthly_payment, payment_frequency, loan_status, last_payment_date, last_payment_amount, next_payment_date, 
            loan_start_date, loan_end_date, created_at, updated_at)
            VALUES 
            (@asset_id, @user_id, @lender_name, @loan_amount, @interest_rate, @loan_term_years, @remaining_balance, 
            @monthly_payment, @payment_frequency, @loan_status, @last_payment_date, @last_payment_amount, @next_payment_date, 
            @loan_start_date, @loan_end_date, @create_date, @update_date);
            SELECT SCOPE_IDENTITY()", conn);
        command.Parameters.AddWithValue("@asset_id", loan.AssetId);
        command.Parameters.AddWithValue("@user_id", loan.UserId);
        command.Parameters.AddWithValue("@lender_name", loan.LenderName);
        command.Parameters.AddWithValue("@loan_amount", loan.LoanAmount);
        command.Parameters.AddWithValue("@interest_rate", loan.InterestRate);
        command.Parameters.AddWithValue("@loan_term_years", loan.LoanTermYears);
        command.Parameters.AddWithValue("@remaining_balance", loan.RemainingBalance);
        command.Parameters.AddWithValue("@monthly_payment", loan.MonthlyPayment);
        command.Parameters.AddWithValue("@payment_frequency", loan.PaymentFrequency);
        command.Parameters.AddWithValue("@loan_status", loan.Status);
        command.Parameters.AddWithValue("@last_payment_date", loan.LastPaymentDate);
        command.Parameters.AddWithValue("@last_payment_amount", loan.LastPaymentAmount);
        command.Parameters.AddWithValue("@next_payment_date", loan.NextPaymentDate);
        command.Parameters.AddWithValue("@loan_start_date", loan.LoanStartDate);
        command.Parameters.AddWithValue("@loan_end_date", loan.LoanEndDate);
        command.Parameters.AddWithValue("@create_date", DateTime.Now);
        command.Parameters.AddWithValue("@update_date", DateTime.Now);

        var loanId = (decimal)await command.ExecuteScalarAsync();
        loan.LoanId = (long)loanId;
      }

      return loan;
    }

    public async Task<LoanInformationDTO> UpdateLoanRecordAsync(LoanInformationDTO loan)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
          @"UPDATE dbo.LoanInformation
            SET asset_id = @asset_id, user_id = @user_id, lender_name = @lender_name, loan_amount = @loan_amount, 
            interest_rate = @interest_rate, loan_term_years = @loan_term_years, remaining_balance = @remaining_balance, 
            monthly_payment = @monthly_payment, payment_frequency = @payment_frequency, loan_status = @loan_status, last_payment_date = @last_payment_date, 
            last_payment_amount = @last_payment_amount, next_payment_date = @next_payment_date, loan_start_date = @loan_start_date, 
            loan_end_date = @loan_end_date, updated_at = @update_date
            WHERE loan_id = @loan_id", conn);
        command.Parameters.AddWithValue("@loan_id", loan.LoanId);
        command.Parameters.AddWithValue("@asset_id", loan.AssetId);
        command.Parameters.AddWithValue("@user_id", loan.UserId);
        command.Parameters.AddWithValue("@lender_name", loan.LenderName);
        command.Parameters.AddWithValue("@loan_amount", loan.LoanAmount);
        command.Parameters.AddWithValue("@interest_rate", loan.InterestRate);
        command.Parameters.AddWithValue("@loan_term_years", loan.LoanTermYears);
        command.Parameters.AddWithValue("@remaining_balance", loan.RemainingBalance);
        command.Parameters.AddWithValue("@monthly_payment", loan.MonthlyPayment);
        command.Parameters.AddWithValue("@payment_frequency", loan.PaymentFrequency);
        command.Parameters.AddWithValue("@loan_status", loan.Status);
        command.Parameters.AddWithValue("@last_payment_date", loan.LastPaymentDate);
        command.Parameters.AddWithValue("@last_payment_amount", loan.LastPaymentAmount);
        command.Parameters.AddWithValue("@next_payment_date", loan.NextPaymentDate);
        command.Parameters.AddWithValue("@loan_start_date", loan.LoanStartDate);
        command.Parameters.AddWithValue("@loan_end_date", loan.LoanEndDate);
        command.Parameters.AddWithValue("@update_date", DateTime.Now);

        int rowsAffected = await command.ExecuteNonQueryAsync();
        if (rowsAffected > 0)
        {
          return loan;
        }
        else
        {
          return null; // No rows updated, return null or handle as needed
        }
      }
    }

    public async Task<bool> DeleteLoanRecordAsync(long loanId)
    {
      using (var conn = new MySqlConnection(_connectionString))
      {
        await conn.OpenAsync();

        var command = new MySqlCommand(
          @"DELETE FROM dbo.LoanInformation
            WHERE loan_id = @loan_id", conn);
        command.Parameters.AddWithValue("@loan_id", loanId);

        int rowsAffected = await command.ExecuteNonQueryAsync();

        return rowsAffected > 0;
      }
    }
    

  }
}
