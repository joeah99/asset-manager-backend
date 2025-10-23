using System;
using System.Numerics;

namespace API.DTOs;

public class LoanInformationDTO {
    public long LoanId { get; set; }
    public required long AssetId { get; set; }
    public required long UserId { get; set; }
    public required string LenderName { get; set; }
    public required float LoanAmount { get; set; }
    public required float InterestRate { get; set; }
    public required int LoanTermYears { get; set; }
    public required float RemainingBalance { get; set; }
    public required float MonthlyPayment { get; set; }
    public required string PaymentFrequency { get; set; }
    public required string Status { get; set; }
    public string? LastPaymentDate { get; set; } = null;
    public float? LastPaymentAmount { get; set; } = null;
    public string? NextPaymentDate { get; set; } = null;
    public string? LoanStartDate { get; set; } = null;
    public string? LoanEndDate { get; set; } = null;
    public List<LoanScheduleDTO> LoanSchedule { get; set; }
    public DateTime LoanCreation { get; set; }
    public DateTime LoanUpdate { get; set; }

}
