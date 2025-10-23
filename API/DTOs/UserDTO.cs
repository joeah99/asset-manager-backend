using System;
using System.Numerics;

namespace API.DTOs;

public class UserDTO {
  public required long UserId { get; set; }
  
  public required string FullName { get; set; }

  public required string Email { get; set; }
  public string? Company { get; set; }
  public required string Username { get; set; }

  public required string Password { get; set; }

  public required DateTime AccountCreation { get; set; }

}
