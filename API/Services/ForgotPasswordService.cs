using System;
using System.Security.Cryptography;
using Isopoh.Cryptography.Argon2;
using API.DbContext;

namespace API.Services
{

  public class ForgotPasswordService {

    private readonly AccountDbContext _accountDbContext;
    private readonly EmailService _emailService;

    public ForgotPasswordService(AccountDbContext accountDbContext, EmailService emailService)
    {
      _accountDbContext = accountDbContext;
      _emailService = emailService;
    }
    public async Task<byte[]> GeneratePasswordResetToken(string email)
    {
      var userExists = await _accountDbContext.UserExists(email);

      if (!userExists)
      {
        return null;
      }

      var resetCode = GenerateAlphanumericCode();
      var resetCodeBytes = System.Text.Encoding.UTF8.GetBytes(resetCode);
      var hash = HashResetToken(resetCodeBytes);

      var result = await _accountDbContext.AddForgotPasswordToken(Convert.ToBase64String(hash), email);

      if (!result)
      {
        return null;
      }
      var emailSent = await _emailService.SendPasswordResetEmail(email, resetCode);
      if (!emailSent)
      {
        return null;
      }
      return hash;
    }

    public async Task<bool> VerifyPasswordResetToken(string resetToken, string email)
    {
      try {

        var trimmedResetToken = System.Text.Encoding.UTF8.GetBytes(resetToken.Trim());
        var resetTokenHash = HashResetToken(trimmedResetToken);

        var databaseToken = await _accountDbContext.VerifyPasswordResetToken(Convert.ToBase64String(resetTokenHash), email);

        if (databaseToken != null)
        {
          return true;
        }
        
        return false;
      } catch (Exception ex) {
        Console.WriteLine("Error verifying password reset token: " + ex.Message);
        return false;
      }
      
    }

    public async Task<bool> ChangePassword(string password, string email)
    {
      try {
        var hashedPassword = Argon2.Hash(password);
        return await _accountDbContext.ChangePassword(hashedPassword, email);
      } catch (Exception ex) {
        return false;
      }
    }

  private byte[] HashResetToken(byte[] resetToken)
    {
      using (SHA256 sha256 = SHA256.Create())
      {
        try {
          byte[] hash = sha256.ComputeHash(resetToken);
          return hash;
        } catch (Exception ex) {
          return null;
        }
      }
    }

    public string GenerateAlphanumericCode()
    {
        var randomBytes = new byte[6];
        using (var rng = RandomNumberGenerator.Create())
        {
            rng.GetBytes(randomBytes);
        }
        return Convert.ToBase64String(randomBytes)
            .Substring(0, 6)
            .Replace("/", "A")
            .Replace("+", "B"); 
    }

  }
  
}