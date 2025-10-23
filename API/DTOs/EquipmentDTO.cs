using System;

namespace API.DTOs;

public class EquipmentDTO
{
  public required string EquipmentType { get; set; }

  public required string Manufacturer { get; set; }

  public required string Model { get; set; }

  public required string Year { get; set; }

  public required string Usage { get; set; }

  public required string Condition { get; set; }

  public required string Country { get; set; }

  public required string State { get; set; }

}
