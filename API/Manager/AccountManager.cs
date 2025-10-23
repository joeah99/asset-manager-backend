using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;
using API.DbContext;
using API.Services;
using System.Security.Cryptography;

namespace API.Managers
{
  public class AccountManager
  {
    private readonly AccountDbContext _accountDbContext;
    private readonly ForgotPasswordService _forgotPasswordService;
    
    public AccountManager(AccountDbContext accountDbContext, ForgotPasswordService forgotPasswordService)
    {
      _accountDbContext = accountDbContext;
      _forgotPasswordService = forgotPasswordService;
    }

    public async Task<byte[]> GeneratePasswordResetToken(string email)
    {
      try {
        return await _forgotPasswordService.GeneratePasswordResetToken(email);
      } catch (Exception ex) {
        return null;
      }
    }

    public async Task<bool> ChangePassword(string password, string email)
    {
      try {
        return await _accountDbContext.ChangePassword(password, email);
      } catch (Exception ex) {
        Console.WriteLine($"Error changing password: {ex.Message}");
        return false;
      }
    }

    public async Task<bool> VerifyPasswordResetToken(string resetToken, string email)
    {
      try {
        return await _forgotPasswordService.VerifyPasswordResetToken(resetToken, email);
      } catch (Exception ex) {
        return false;
      }
    }

  }

}