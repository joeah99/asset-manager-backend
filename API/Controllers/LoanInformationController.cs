using API.DbContext;
using API.DTOs;
using API.Managers;
using API.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace API.Controllers
{
    [ApiController]
    public class LoanInformationController : ControllerBase
    {
        private readonly LoanManager _loanManager;
        public LoanInformationController(LoanManager loanManager)
        {
            _loanManager = loanManager;
        }

        [HttpPost("CreateLoanRecord")]
        public async Task<ActionResult<LoanInformationDTO>> CreateLoanRecord([FromBody] LoanInformationDTO loan)
        {
            var newLoan = await _loanManager.CreateLoan(loan);

            if (newLoan != null) {
                return Ok(new { loan = newLoan, message = "Loan created successfully." });
            } else {
                return NotFound("Loan creation failed.");
            }
        }
        

        [HttpPost("GetLoans")]
        public async Task<ActionResult<List<LoanInformationDTO>>> GetLoans([FromBody] long user_id)
        {
            var loans = await _loanManager.GetLoans(user_id);

            if (loans != null)
            {
                return Ok(loans);
            } else
            {
                return NotFound("No loan data found.");
            }
        }

        [HttpPut("UpdateLoan")]
        public async Task<ActionResult<LoanInformationDTO>> UpdateLoan([FromBody] LoanInformationDTO loan)
        {
            try
            {
                var result = await _loanManager.UpdateLoan(loan);
                if (result != null)
                {
                    return Ok(new { loan = result, message = "Loan updated successfully" });
                }
                else
                {
                    return StatusCode(StatusCodes.Status500InternalServerError, new { message = "Error updating loan" });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

        [HttpDelete("DeleteLoan")]
        public async Task<ActionResult> DeleteLoan([FromBody] long loanId)
        {
            try
            {
                var result = await _loanManager.DeleteLoan(loanId);
                if (result)
                {
                    return Ok(new { message = "Loan deleted successfully" });
                }
                else
                {
                    return StatusCode(StatusCodes.Status500InternalServerError, new { message = "Error deleting loan" });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = ex.Message });
            }
        }

    }
}
