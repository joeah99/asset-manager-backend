using System.Numerics;
using System.Text.Json.Serialization;

namespace API.DTOs;

public class VehicleValuationDTO {
  public long LogId { get; set; }

  public long AssetId { get; set; }
  
  [JsonPropertyName("unadjustedLow")]
  public double? UnadjustedLow { get; set; }

  [JsonPropertyName("unadjustedHigh")]
  public double? UnadjustedHigh { get; set; }
  
  [JsonPropertyName("unadjustedFinance")]
  public double? UnadjustedFinance { get; set; }

  [JsonPropertyName("unadjustedRetail")]
  public double? UnadjustedRetail { get; set; }
  
  [JsonPropertyName("unadjustedWholesale")]
  public double? UnadjustedWholesale { get; set; }
  
  [JsonPropertyName("unadjustedTradeIn")]
  public double? UnadjustedTradeIn { get; set; }

  [JsonPropertyName("adjustedLow")]
  public double? AdjustedLow { get; set; }

  [JsonPropertyName("adjustedHigh")]
  public double? AdjustedHigh { get; set; }
  
  [JsonPropertyName("adjustedFinance")]
  public double? AdjustedFinance { get; set; }

  [JsonPropertyName("adjustedRetail")]
  public double? AdjustedRetail { get; set; }
  
  [JsonPropertyName("adjustedWholesale")]
  public double? AdjustedWholesale { get; set; }
  
  [JsonPropertyName("adjustedTradeIn")]
  public double? AdjustedTradeIn { get; set; }

  public DateTime ValuationDate { get; set; }

}
