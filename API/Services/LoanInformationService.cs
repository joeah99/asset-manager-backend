using System;
using API.DTOs;

namespace API.Services
{
    public class LoanInformationService 
    {
        public float CalculateMonthlyPayment(float loanAmount, float interestRate, int loanTermYears)
        {
            float monthlyInterestRate = interestRate / 1200;
            int totalPayments = loanTermYears * 12;
            float monthlyPayment = ((loanAmount * monthlyInterestRate) / (1 - (float)Math.Pow(1 + monthlyInterestRate, -totalPayments)));
            return monthlyPayment;
        }

        public List<LoanScheduleDTO> GenerateLoanSchedule(LoanInformationDTO loan)
        {
            var schedule = new List<LoanScheduleDTO>();
            float remainingBalance = loan.LoanAmount;
            float monthlyPayment = loan.MonthlyPayment;

            // Parse start and end dates or default to today and loan term
            DateTime startDate = !string.IsNullOrEmpty(loan.LoanStartDate) && DateTime.TryParse(loan.LoanStartDate, out var parsedStartDate)
                ? parsedStartDate
                : DateTime.Today;

            DateTime endDate = !string.IsNullOrEmpty(loan.LoanEndDate) && DateTime.TryParse(loan.LoanEndDate, out var parsedEndDate)
                ? parsedEndDate
                : startDate.AddMonths(loan.LoanTermYears * 12);

            DateTime currentDate = startDate.AddMonths(1); // Start from the next month after the loan start date

            while (remainingBalance > 0 && currentDate <= endDate)
            {
                // Ensure the last payment doesn't overpay
                if (monthlyPayment > remainingBalance)
                {
                    remainingBalance = 0;
                    monthlyPayment = remainingBalance;
                }

                remainingBalance -= monthlyPayment;

                schedule.Add(new LoanScheduleDTO
                {
                    LoanPaymentDate = currentDate.ToString("yyyy-MM-dd"),
                    NewRemainingValue = remainingBalance
                });
                currentDate = currentDate.AddMonths(1);
            }

            return schedule;
        }
    }
}