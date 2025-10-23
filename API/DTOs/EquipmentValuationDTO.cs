using System.Numerics;
using System.Text.Json.Serialization;

namespace API.DTOs;

public class EquipmentValuationDTO {
  public long LogId { get; set; }

  public long AssetId { get; set; }
  
  [JsonPropertyName("unadjustedFmv")]
  public double? UnadjustedFairMarketValue { get; set; }

  [JsonPropertyName("unadjustedOlv")]
  public double? UnadjustedOrderlyLiquidationValue { get; set; }
  
  [JsonPropertyName("unadjustedFlv")]
  public double? UnadjustedForcedLiquidationValue { get; set; }

  [JsonPropertyName("adjustedFmv")]
  public double? AdjustedFairMarketValue { get; set; }
  
  [JsonPropertyName("adjustedOlv")]
  public double? AdjustedOrderlyLiquidationValue { get; set; }
  
  [JsonPropertyName("adjustedFlv")]
  public double? AdjustedForcedLiquidationValue { get; set; }
  
  [JsonPropertyName("salvage")]
  public double? Salvage { get; set; }

  public DateTime ValuationDate { get; set; }

}
