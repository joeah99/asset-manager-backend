namespace API.DTOs
{
    public class AssetDepreciationScheduleDTO
    {
        public required long AssetDepreciationScheduleId { get; set; }
        public required long AssetId { get; set; }
        public required string DepreciationDate { get; set; }
        public required float NewBookValue { get; set; }
        public required DateTime CreatedAt { get; set; }
    }
}
