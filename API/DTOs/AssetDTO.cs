namespace API.DTOs
{
  public class AssetDTO
  {
    public long AssetId { get; set; }
    public long UserId { get; set; }
    public string Type { get; set; }
    public float BookValue { get; set; }
    public string Manufacturer { get; set; }
    public string Model { get; set; }
    public string ModelYear { get; set; }
    public int Usage { get; set; }
    public string Condition { get; set; }
    public string Country { get; set; }
    public string State { get; set; }
    public bool Deleted { get; set; }
    public string DepreciationMethod { get; set; }
    public float SalvageValue { get; set; }
    public int? UsefulLife { get; set; }
    public float? DepreciationRate { get; set; }
    public int? TotalExpectedUnitsOfProduction { get; set; }
    public int? UnitsProducedInYear { get; set; }
    public string CreateDate { get; set; }
    public string UpdateDate { get; set; }
    public List<FairMarketValueDTO> fairMarketValuesOverTime { get; set; }
    public List<AssetDepreciationDTO> assetDepreciationSchedule { get; set; }

  }
}


