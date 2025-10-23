using System.Text.Json.Serialization;

namespace API.DTOs;

public class AdjustedForcedLiquidation
{
  public long AssetId { get; set; }

  public DateTime ValuationDate { get; set; }

  [JsonPropertyName("adjustedFlv")]
  public double? AdjustedForcedLiquidationValue { get; set; }
}