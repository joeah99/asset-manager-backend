using Npgsql;
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

            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"SELECT 
                        loan_id, asset_id, user_id, lender_name, loan_amount, interest_rate, loan_term_years, 
                        remaining_balance, monthly_payment, payment_frequency, loan_status, 
                        last_payment_date, last_payment_amount, next_payment_date, 
                        loan_start_date, loan_end_date, created_at, updated_at
                      FROM ""LoanInformation""
                      WHERE user_id = @user_id;", conn);
                command.Parameters.AddWithValue("@user_id", user_id);

                await using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        var loan = new LoanInformationDTO
                        {
                            LoanId = reader.GetInt64(reader.GetOrdinal("loan_id")),
                            AssetId = reader.GetInt64(reader.GetOrdinal("asset_id")),
                            UserId = reader.GetInt64(reader.GetOrdinal("user_id")),
                            LenderName = reader.IsDBNull(reader.GetOrdinal("lender_name")) ? string.Empty : reader.GetString(reader.GetOrdinal("lender_name")),
                            LoanAmount = reader.IsDBNull(reader.GetOrdinal("loan_amount")) ? 0 : (float)reader.GetDouble(reader.GetOrdinal("loan_amount")),
                            InterestRate = reader.IsDBNull(reader.GetOrdinal("interest_rate")) ? 0 : (float)reader.GetDouble(reader.GetOrdinal("interest_rate")),
                            LoanTermYears = reader.IsDBNull(reader.GetOrdinal("loan_term_years")) ? 0 : reader.GetInt32(reader.GetOrdinal("loan_term_years")),
                            RemainingBalance = reader.IsDBNull(reader.GetOrdinal("remaining_balance")) ? 0 : (float)reader.GetDouble(reader.GetOrdinal("remaining_balance")),
                            MonthlyPayment = reader.IsDBNull(reader.GetOrdinal("monthly_payment")) ? 0 : (float)reader.GetDouble(reader.GetOrdinal("monthly_payment")),
                            PaymentFrequency = reader.IsDBNull(reader.GetOrdinal("payment_frequency")) ? string.Empty : reader.GetString(reader.GetOrdinal("payment_frequency")),
                            Status = reader.IsDBNull(reader.GetOrdinal("loan_status")) ? string.Empty : reader.GetString(reader.GetOrdinal("loan_status")),
                            LastPaymentDate = reader.IsDBNull(reader.GetOrdinal("last_payment_date")) ? string.Empty : reader.GetString(reader.GetOrdinal("last_payment_date")),
                            LastPaymentAmount = reader.IsDBNull(reader.GetOrdinal("last_payment_amount")) ? 0 : (float)reader.GetDouble(reader.GetOrdinal("last_payment_amount")),
                            NextPaymentDate = reader.IsDBNull(reader.GetOrdinal("next_payment_date")) ? string.Empty : reader.GetString(reader.GetOrdinal("next_payment_date")),
                            LoanStartDate = reader.IsDBNull(reader.GetOrdinal("loan_start_date")) ? string.Empty : reader.GetString(reader.GetOrdinal("loan_start_date")),
                            LoanEndDate = reader.IsDBNull(reader.GetOrdinal("loan_end_date")) ? string.Empty : reader.GetString(reader.GetOrdinal("loan_end_date")),
                            LoanCreation = reader.IsDBNull(reader.GetOrdinal("created_at")) ? DateTime.MinValue : reader.GetDateTime(reader.GetOrdinal("created_at")),
                            LoanUpdate = reader.IsDBNull(reader.GetOrdinal("updated_at")) ? DateTime.MinValue : reader.GetDateTime(reader.GetOrdinal("updated_at"))
                        };

                        loanList.Add(loan);
                    }
                }
            }

            return loanList;
        }

        public async Task<LoanInformationDTO?> CreateLoanRecordAsync(LoanInformationDTO loan)
        {
            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"INSERT INTO ""LoanInformation""
                        (asset_id, user_id, lender_name, loan_amount, interest_rate, loan_term_years, 
                        remaining_balance, monthly_payment, payment_frequency, loan_status, 
                        last_payment_date, last_payment_amount, next_payment_date, 
                        loan_start_date, loan_end_date, created_at, updated_at)
                      VALUES 
                        (@asset_id, @user_id, @lender_name, @loan_amount, @interest_rate, @loan_term_years, 
                        @remaining_balance, @monthly_payment, @payment_frequency, @loan_status, 
                        @last_payment_date, @last_payment_amount, @next_payment_date, 
                        @loan_start_date, @loan_end_date, NOW(), NOW())
                      RETURNING loan_id;", conn);

                command.Parameters.AddWithValue("@asset_id", loan.AssetId);
                command.Parameters.AddWithValue("@user_id", loan.UserId);
                command.Parameters.AddWithValue("@lender_name", loan.LenderName ?? string.Empty);
                command.Parameters.AddWithValue("@loan_amount", loan.LoanAmount);
                command.Parameters.AddWithValue("@interest_rate", loan.InterestRate);
                command.Parameters.AddWithValue("@loan_term_years", loan.LoanTermYears);
                command.Parameters.AddWithValue("@remaining_balance", loan.RemainingBalance);
                command.Parameters.AddWithValue("@monthly_payment", loan.MonthlyPayment);
                command.Parameters.AddWithValue("@payment_frequency", loan.PaymentFrequency ?? string.Empty);
                command.Parameters.AddWithValue("@loan_status", loan.Status ?? string.Empty);
                command.Parameters.AddWithValue("@last_payment_date", loan.LastPaymentDate ?? string.Empty);
                command.Parameters.AddWithValue("@last_payment_amount", loan.LastPaymentAmount);
                command.Parameters.AddWithValue("@next_payment_date", loan.NextPaymentDate ?? string.Empty);
                command.Parameters.AddWithValue("@loan_start_date", loan.LoanStartDate ?? string.Empty);
                command.Parameters.AddWithValue("@loan_end_date", loan.LoanEndDate ?? string.Empty);

                var loanId = (long)(await command.ExecuteScalarAsync() ?? 0);
                loan.LoanId = loanId;

                return loan;
            }
        }

        public async Task<LoanInformationDTO?> UpdateLoanRecordAsync(LoanInformationDTO loan)
        {
            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"UPDATE ""LoanInformation""
                      SET asset_id = @asset_id,
                          user_id = @user_id,
                          lender_name = @lender_name,
                          loan_amount = @loan_amount,
                          interest_rate = @interest_rate,
                          loan_term_years = @loan_term_years,
                          remaining_balance = @remaining_balance,
                          monthly_payment = @monthly_payment,
                          payment_frequency = @payment_frequency,
                          loan_status = @loan_status,
                          last_payment_date = @last_payment_date,
                          last_payment_amount = @last_payment_amount,
                          next_payment_date = @next_payment_date,
                          loan_start_date = @loan_start_date,
                          loan_end_date = @loan_end_date,
                          updated_at = NOW()
                      WHERE loan_id = @loan_id;", conn);

                command.Parameters.AddWithValue("@loan_id", loan.LoanId);
                command.Parameters.AddWithValue("@asset_id", loan.AssetId);
                command.Parameters.AddWithValue("@user_id", loan.UserId);
                command.Parameters.AddWithValue("@lender_name", loan.LenderName ?? string.Empty);
                command.Parameters.AddWithValue("@loan_amount", loan.LoanAmount);
                command.Parameters.AddWithValue("@interest_rate", loan.InterestRate);
                command.Parameters.AddWithValue("@loan_term_years", loan.LoanTermYears);
                command.Parameters.AddWithValue("@remaining_balance", loan.RemainingBalance);
                command.Parameters.AddWithValue("@monthly_payment", loan.MonthlyPayment);
                command.Parameters.AddWithValue("@payment_frequency", loan.PaymentFrequency ?? string.Empty);
                command.Parameters.AddWithValue("@loan_status", loan.Status ?? string.Empty);
                command.Parameters.AddWithValue("@last_payment_date", loan.LastPaymentDate ?? string.Empty);
                command.Parameters.AddWithValue("@last_payment_amount", loan.LastPaymentAmount);
                command.Parameters.AddWithValue("@next_payment_date", loan.NextPaymentDate ?? string.Empty);
                command.Parameters.AddWithValue("@loan_start_date", loan.LoanStartDate ?? string.Empty);
                command.Parameters.AddWithValue("@loan_end_date", loan.LoanEndDate ?? string.Empty);

                var rowsAffected = await command.ExecuteNonQueryAsync();
                return rowsAffected > 0 ? loan : null;
            }
        }

        public async Task<bool> DeleteLoanRecordAsync(long loanId)
        {
            await using (var conn = new NpgsqlConnection(_connectionString))
            {
                await conn.OpenAsync();

                var command = new NpgsqlCommand(
                    @"DELETE FROM ""LoanInformation"" WHERE loan_id = @loan_id;", conn);
                command.Parameters.AddWithValue("@loan_id", loanId);

                var rowsAffected = await command.ExecuteNonQueryAsync();
                return rowsAffected > 0;
            }
        }
    }
}
