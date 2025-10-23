namespace API.DTOs
{
    public class ColumnPreferencesDto
    {
        public required long UserId { get; set; }
        public required string Preferences { get; set; }
    }
} 