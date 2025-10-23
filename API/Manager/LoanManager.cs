using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;
using API.DbContext;
using API.Services;

namespace API.Managers
{
    public class LoanManager
    {
        private readonly LoanInformationDbContext _dbContext;
        private readonly LoanProjectedPaymentsDbContext _loanProjectedPaymentsDbContext;
        private readonly LoanInformationService _loanInformationService;

        public LoanManager(LoanInformationDbContext dbContext, LoanProjectedPaymentsDbContext loanProjectedPaymentsDbContext, LoanInformationService loanInformationService)
        {
            _dbContext = dbContext;
            _loanProjectedPaymentsDbContext = loanProjectedPaymentsDbContext;
            _loanInformationService = loanInformationService;
        }

        public async Task<List<LoanInformationDTO>> GetLoans(long user_id)
        {
            var loanList = await _dbContext.GetLoansAsync(user_id);
            var loanProjectedPaymentsList = await _loanProjectedPaymentsDbContext.GetLoanProjectedPaymentsByUserIdAsync(user_id);
            var loanProjectedPaymentsByLoan = loanProjectedPaymentsList
                .GroupBy(lp => lp.LoanId)
                .ToDictionary(
                    g => g.Key,
                    g => g.Select(lp => new LoanScheduleDTO
                    {
                        LoanPaymentDate = lp.LoanPaymentDate,
                        NewRemainingValue = (float)lp.NewRemainingValue
                    }).ToList()
                );

            var result = loanList.Select(loan => new LoanInformationDTO
            {
                LoanId = loan.LoanId,
                AssetId = loan.AssetId,
                UserId = loan.UserId,
                LenderName = loan.LenderName,
                LoanAmount = loan.LoanAmount,
                InterestRate = loan.InterestRate,
                LoanTermYears = loan.LoanTermYears,
                RemainingBalance = loanProjectedPaymentsByLoan.ContainsKey(loan.LoanId)
                    ? loanProjectedPaymentsByLoan[loan.LoanId]
                        .Where(p => DateTime.Parse(p.LoanPaymentDate).Year == DateTime.Now.Year && DateTime.Parse(p.LoanPaymentDate).Month == DateTime.Now.Month)
                        .OrderByDescending(p => DateTime.Parse(p.LoanPaymentDate))
                        .FirstOrDefault()?.NewRemainingValue ?? loan.RemainingBalance
                    : loan.RemainingBalance,
                MonthlyPayment = loan.MonthlyPayment,
                PaymentFrequency = loan.PaymentFrequency,
                Status = loan.Status,
                LastPaymentDate = loan.LastPaymentDate,
                LastPaymentAmount = loan.LastPaymentAmount,
                NextPaymentDate = loan.NextPaymentDate,
                LoanStartDate = loan.LoanStartDate.ToString(),
                LoanEndDate = loan.LoanEndDate.ToString(),
                LoanSchedule = loanProjectedPaymentsByLoan.ContainsKey(loan.LoanId) ? loanProjectedPaymentsByLoan[loan.LoanId] : new List<LoanScheduleDTO>(),
                LoanCreation = DateTime.Now,
                LoanUpdate = DateTime.Now
            }).ToList();
            return result;
        }

        public async Task<LoanInformationDTO> CreateLoan(LoanInformationDTO loan)
        {
            loan.MonthlyPayment = _loanInformationService.CalculateMonthlyPayment(loan.LoanAmount, loan.InterestRate, loan.LoanTermYears);
            if(string.IsNullOrEmpty(loan.NextPaymentDate))
            {
                loan.NextPaymentDate = DateTime.Now.AddMonths(1).ToString("yyyy-MM-dd");
            }
            if(string.IsNullOrEmpty(loan.LoanStartDate))
            {
                loan.LoanStartDate = DateTime.Now.ToString("yyyy-MM-dd");
            }
            if(string.IsNullOrEmpty(loan.LoanEndDate))
            {
                loan.LoanEndDate = DateTime.Now.AddYears(loan.LoanTermYears).ToString("yyyy-MM-dd");
            }
            var newLoan = await _dbContext.CreateLoanRecordAsync(loan);
            List<LoanScheduleDTO> loanSchedule = _loanInformationService.GenerateLoanSchedule(newLoan);
            foreach (var schedule in loanSchedule)
            {
                var loanProjectedPayment = new LoanProjectedPaymentsDTO
                {
                    LoanProjectedPaymentId = 0,
                    LoanId = newLoan.LoanId,
                    LoanPaymentDate = schedule.LoanPaymentDate,
                    NewRemainingValue = schedule.NewRemainingValue,
                    CreatedAt = DateTime.Now
                };
                await _loanProjectedPaymentsDbContext.CreateLoanProjectedPaymentsAsync(loanProjectedPayment);
            }
            newLoan.LoanSchedule = loanSchedule;
            newLoan.LoanCreation = DateTime.Now;
            newLoan.LoanUpdate = DateTime.Now;
            return newLoan;
        }

        public async Task<LoanInformationDTO> UpdateLoan(LoanInformationDTO loan)
        {
            loan.MonthlyPayment = _loanInformationService.CalculateMonthlyPayment(loan.LoanAmount, loan.InterestRate, loan.LoanTermYears);
            var updatedLoan = await _dbContext.UpdateLoanRecordAsync(loan);

            var deletedLoanProjectedPayments = await _loanProjectedPaymentsDbContext.DeleteLoanProjectedPaymentsAsync(updatedLoan.LoanId);
            if (deletedLoanProjectedPayments == false)
            {
                throw new Exception("Failed to delete existing loan projected payments.");
            }
            List<LoanScheduleDTO> loanSchedule = _loanInformationService.GenerateLoanSchedule(updatedLoan);
            foreach (var schedule in loanSchedule)
            {
                var loanProjectedPayment = new LoanProjectedPaymentsDTO
                {
                    LoanProjectedPaymentId = 0,
                    LoanId = updatedLoan.LoanId,
                    LoanPaymentDate = schedule.LoanPaymentDate,
                    NewRemainingValue = schedule.NewRemainingValue,
                    CreatedAt = DateTime.Now
                };
                await _loanProjectedPaymentsDbContext.CreateLoanProjectedPaymentsAsync(loanProjectedPayment);
            }
            updatedLoan.LoanSchedule = loanSchedule;
            updatedLoan.LoanUpdate = DateTime.Now;
            return updatedLoan;
        }

        public async Task<bool> DeleteLoan(long loanId)
        {
            var result = await _dbContext.DeleteLoanRecordAsync(loanId);
            return result;
        }
    }
    
}