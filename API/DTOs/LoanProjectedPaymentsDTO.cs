namespace API.DTOs
{
    public class LoanProjectedPaymentsDTO
    {
        public required long LoanProjectedPaymentId { get; set; }
        public required long LoanId { get; set; }
        public required string LoanPaymentDate { get; set; }
        public required float NewRemainingValue { get; set; }
        public required DateTime CreatedAt { get; set; }
    }
}
