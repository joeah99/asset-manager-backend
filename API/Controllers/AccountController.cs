using API.DbContext;
using API.DTOs;
using Isopoh.Cryptography.Argon2;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using API.Managers;

namespace API.Controllers
{
    [ApiController]
    public class AccountController : ControllerBase
    {
        private readonly AccountDbContext _accountDbContext;
        private readonly AccountManager _accountManager;
        public AccountController(AccountDbContext accountDbContext, AccountManager accountManager)
        {
            _accountDbContext = accountDbContext;
            _accountManager = accountManager;
        }

        [HttpPost("Register")]
        public async Task<ActionResult<AppUser>> Register([FromBody] RegisterDto registerDto)
        {
            try
            {
                if (await UserExists(registerDto.Email))
                    return BadRequest(new { message = "Account with this email already exists" });
                var usernameExistsResult = await CheckIfUserNameExists(registerDto.Username);
                if (usernameExistsResult.Value)
                    return BadRequest(new { message = "Account with this username already exists" });
                var user = new AppUser
                {
                    FullName = $"{registerDto.FirstName} {registerDto.LastName}",
                    Username = registerDto.Username,
                    Email = registerDto.Email,
                    PasswordHash = Argon2.Hash(registerDto.Password)
                };

                var createdUser = await _accountDbContext.RegisterUser(user);

                return Ok(createdUser);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        [HttpPost("Login")]
        public async Task<ActionResult<AppUser>> Login([FromBody] LoginDto loginDto)
        {
            try
            {
                if (await UserExists(loginDto.Email))
                {
                    var isPasswordValid = await _accountDbContext.IsPasswordValid(loginDto);

                    if (!isPasswordValid)
                    {
                        return Unauthorized(new { message = "Invalid Password" });
                    }

                    var user = await _accountDbContext.GetUserByUsername(loginDto.Email);

                    if (user == null)
                    {
                        return NotFound(new { message = "User not found" });
                    }

                    return Ok(user);
                }

                return BadRequest(new { message = "Username does not exist" });
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        [HttpGet("CheckUsernameExists")]
        public async Task<ActionResult<bool>> CheckIfUserNameExists(string username)
        {
            try
            {
                var response = await UserNameExists(username);

                return response
                    ? true
                    : false;
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        [HttpDelete("DeleteUser")]
        public async Task<ActionResult> DeleteUser([FromBody] string email)
        {
            try
            {
                var userExists = await UserExists(email);
                if (!userExists)
                {
                    return NotFound(new { message = "User not found" });
                }

                var result = await _accountDbContext.DeleteUser(email);
                if (result)
                {
                    return Ok(new { message = "User deleted successfully" });
                }
                else
                {
                    return StatusCode(StatusCodes.Status500InternalServerError, new { message = "Error deleting user" });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        [HttpPut("UpdateUser")]
        public async Task<ActionResult> UpdateUser([FromBody] AppUser user)
        {
            try
            {
                var result = await _accountDbContext.UpdateUser(user);
                if (result)
                {
                    return Ok(new { message = "User updated successfully" });
                }
                else
                {
                    return StatusCode(StatusCodes.Status500InternalServerError, new { message = "Error updating user" });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        [HttpPost("ForgotPassword")]
        public async Task<ActionResult> ForgotPassword([FromBody] string email)
        {
            try {
                var passwordResetToken = await _accountManager.GeneratePasswordResetToken(email);
                if (passwordResetToken == null)
                {
                    return StatusCode(StatusCodes.Status500InternalServerError, new { message = "Error generating password reset token" });
                } else
                {
                    return Ok(new { message = "Password reset token generated successfully" });
                }
            }
            catch (Exception ex) {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        [HttpPost("EnterResetToken")]
        public async Task<ActionResult> EnterResetToken([FromBody] VerifyResetTokenDTO verifyResetTokenDTO)
        {
            try {
                var tokenVerified = await _accountManager.VerifyPasswordResetToken(verifyResetTokenDTO.Token, verifyResetTokenDTO.Email);
                if (!tokenVerified)
                {
                    return StatusCode(StatusCodes.Status500InternalServerError, new { message = "Invalid password reset token" });
                } else
                {
                    return Ok(new { message = "Password reset token verified successfully" });
                }
            }
            catch (Exception ex) {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }

        }

        [HttpPut("ChangePassword")]
        public async Task<ActionResult> ChangePassword([FromBody] ChangePasswordDTO changePasswordDTO)
        {
            string passwordHash = Argon2.Hash(changePasswordDTO.Password);
            try {
                var passwordChanged = await _accountManager.ChangePassword(passwordHash, changePasswordDTO.Email);
                if (!passwordChanged)
                {
                    return StatusCode(StatusCodes.Status500InternalServerError, new { message = "Error changing password" });
                } else
                {
                    return Ok(new { message = "Password changed successfully" });
                }
            }
            catch (Exception ex) {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }   

        [HttpPost("SaveColumnPreferences")]
        public async Task<ActionResult> SaveColumnPreferences([FromBody] ColumnPreferencesDto preferences)
        {
            try
            {
                var result = await _accountDbContext.SaveUserColumnPreferences(preferences.UserId, preferences.Preferences);
                if (result)
                {
                    return Ok(new { message = "Column preferences saved successfully" });
                }
                else
                {
                    return StatusCode(StatusCodes.Status500InternalServerError, new { message = "Error saving column preferences" });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        [HttpGet("GetColumnPreferences/{userId}")]
        public async Task<ActionResult> GetColumnPreferences(long userId)
        {
            try
            {
                var preferences = await _accountDbContext.GetUserColumnPreferences(userId);
                if (preferences != null)
                {
                    return Ok(new { preferences });
                }
                else
                {
                    return NotFound(new { message = "No column preferences found" });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        private async Task<bool> UserExists(string email)
        {
            return await _accountDbContext.UserExists(email);
        }

        private async Task<bool> UserNameExists(string username)
        {
            return await _accountDbContext.UsernameExists(username);
        }

    }

}
