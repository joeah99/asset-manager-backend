import pytest
from datetime import datetime
from services.loan_service import LoanInformationService
from models.loan_models import LoanInformationDTO


@pytest.fixture
def loan_service():
    """Fixture to create a LoanInformationService instance"""
    return LoanInformationService()


@pytest.fixture
def sample_loan():
    """Fixture to create a sample loan for testing"""
    return LoanInformationDTO(
        loan_id=1,
        asset_id=100,
        user_id=1,
        lender_name="Test Bank",
        loan_amount=100000.0,
        interest_rate=5.0,
        loan_term_years=5,
        remaining_balance=100000.0,
        monthly_payment=0.0,  # Will be calculated
        payment_frequency="Monthly",
        status="Active",
        loan_start_date="2024-01-01",
        loan_end_date="2029-01-01"
    )


class TestCalculateMonthlyPayment:
    """Tests for calculate_monthly_payment method"""

    def test_calculate_monthly_payment_valid_inputs(self, loan_service):
        """Test monthly payment calculation with valid inputs"""
        # For a $100,000 loan at 5% APR for 5 years
        # Expected monthly payment is approximately $1,887.12
        monthly_payment = loan_service.calculate_monthly_payment(
            loan_amount=100000.0,
            interest_rate=5.0,
            loan_term_years=5
        )

        assert round(monthly_payment, 2) == 1887.12

    def test_calculate_monthly_payment_zero_interest(self, loan_service):
        """Test monthly payment calculation with zero interest rate"""
        monthly_payment = loan_service.calculate_monthly_payment(
            loan_amount=12000.0,
            interest_rate=0.0,
            loan_term_years=1
        )

        # With 0% interest, payment should be loan amount / months
        assert monthly_payment == 1000.0

    def test_calculate_monthly_payment_high_interest(self, loan_service):
        """Test monthly payment calculation with high interest rate"""
        monthly_payment = loan_service.calculate_monthly_payment(
            loan_amount=50000.0,
            interest_rate=15.0,
            loan_term_years=3
        )

        # Should be a reasonable value > principal/months due to high interest
        assert monthly_payment > (50000.0 / 36)
        assert monthly_payment < 2000.0  # Sanity check


class TestGenerateLoanSchedule:
    """Tests for generate_loan_schedule method (simplified version)"""

    def test_generate_loan_schedule_creates_entries(self, loan_service, sample_loan):
        """Test that loan schedule is generated with correct number of entries"""
        sample_loan.monthly_payment = 1887.12

        schedule = loan_service.generate_loan_schedule(sample_loan)

        # Should have entries for 5 years = 60 months
        assert len(schedule) > 0
        assert len(schedule) <= 60

    def test_generate_loan_schedule_decreasing_balance(self, loan_service, sample_loan):
        """Test that remaining balance decreases over time"""
        sample_loan.monthly_payment = 1887.12

        schedule = loan_service.generate_loan_schedule(sample_loan)

        # Check that balance decreases monotonically
        for i in range(len(schedule) - 1):
            current_balance = schedule[i].new_remaining_value
            next_balance = schedule[i + 1].new_remaining_value
            assert next_balance <= current_balance

    def test_generate_loan_schedule_ends_at_zero(self, loan_service, sample_loan):
        """Test that loan schedule ends with zero or near-zero balance"""
        sample_loan.monthly_payment = 1887.12

        schedule = loan_service.generate_loan_schedule(sample_loan)

        # Last payment should have minimal remaining balance
        final_balance = schedule[-1].new_remaining_value
        assert final_balance < 10.0  # Allow for some rounding


class TestGenerateAmortizationSchedule:
    """Tests for generate_amortization_schedule method (proper version)"""

    def test_amortization_schedule_has_correct_structure(self, loan_service, sample_loan):
        """Test that amortization schedule has all required fields"""
        sample_loan.monthly_payment = loan_service.calculate_monthly_payment(
            sample_loan.loan_amount,
            sample_loan.interest_rate,
            sample_loan.loan_term_years
        )

        schedule = loan_service.generate_amortization_schedule(sample_loan)

        # Check first payment has all required fields
        assert len(schedule) > 0
        first_payment = schedule[0]
        assert "payment_number" in first_payment
        assert "payment_date" in first_payment
        assert "payment_amount" in first_payment
        assert "principal_payment" in first_payment
        assert "interest_payment" in first_payment
        assert "remaining_balance" in first_payment

    def test_amortization_interest_decreases_over_time(self, loan_service, sample_loan):
        """Test that interest portion decreases over time (hallmark of amortization)"""
        sample_loan.monthly_payment = loan_service.calculate_monthly_payment(
            sample_loan.loan_amount,
            sample_loan.interest_rate,
            sample_loan.loan_term_years
        )

        schedule = loan_service.generate_amortization_schedule(sample_loan)

        # Interest should decrease as principal is paid down
        first_interest = schedule[0]["interest_payment"]
        last_interest = schedule[-1]["interest_payment"]
        assert last_interest < first_interest

    def test_amortization_principal_increases_over_time(self, loan_service, sample_loan):
        """Test that principal portion increases over time"""
        sample_loan.monthly_payment = loan_service.calculate_monthly_payment(
            sample_loan.loan_amount,
            sample_loan.interest_rate,
            sample_loan.loan_term_years
        )

        schedule = loan_service.generate_amortization_schedule(sample_loan)

        # Principal should increase as interest decreases
        first_principal = schedule[0]["principal_payment"]
        middle_index = len(schedule) // 2
        middle_principal = schedule[middle_index]["principal_payment"]
        assert middle_principal > first_principal

    def test_amortization_payment_equals_interest_plus_principal(self, loan_service, sample_loan):
        """Test that payment amount equals interest + principal for each period"""
        sample_loan.monthly_payment = loan_service.calculate_monthly_payment(
            sample_loan.loan_amount,
            sample_loan.interest_rate,
            sample_loan.loan_term_years
        )

        schedule = loan_service.generate_amortization_schedule(sample_loan)

        # Check a few random payments
        for payment in schedule[::10]:  # Every 10th payment
            calculated_payment = payment["interest_payment"] + payment["principal_payment"]
            # Allow for small rounding differences
            assert abs(payment["payment_amount"] - calculated_payment) < 0.02


class TestCalculateLoanPayoff:
    """Tests for calculate_loan_payoff method"""

    def test_payoff_at_loan_start(self, loan_service, sample_loan):
        """Test payoff calculation at loan start date"""
        sample_loan.monthly_payment = loan_service.calculate_monthly_payment(
            sample_loan.loan_amount,
            sample_loan.interest_rate,
            sample_loan.loan_term_years
        )

        payoff = loan_service.calculate_loan_payoff(
            loan=sample_loan,
            payoff_date="2024-01-01",
            prepayment_penalty_rate=0.0
        )

        # At start, should owe full amount
        assert payoff["remaining_balance"] == sample_loan.loan_amount
        assert payoff["total_interest_paid"] == 0.0
        assert payoff["total_principal_paid"] == 0.0

    def test_payoff_after_one_year(self, loan_service, sample_loan):
        """Test payoff calculation after one year of payments"""
        sample_loan.monthly_payment = loan_service.calculate_monthly_payment(
            sample_loan.loan_amount,
            sample_loan.interest_rate,
            sample_loan.loan_term_years
        )

        payoff = loan_service.calculate_loan_payoff(
            loan=sample_loan,
            payoff_date="2025-01-01",
            prepayment_penalty_rate=0.0
        )

        # After 1 year, should have paid down some principal
        assert payoff["remaining_balance"] < sample_loan.loan_amount
        assert payoff["total_interest_paid"] > 0.0
        assert payoff["total_principal_paid"] > 0.0

    def test_payoff_with_prepayment_penalty(self, loan_service, sample_loan):
        """Test payoff calculation with prepayment penalty"""
        sample_loan.monthly_payment = loan_service.calculate_monthly_payment(
            sample_loan.loan_amount,
            sample_loan.interest_rate,
            sample_loan.loan_term_years
        )

        payoff = loan_service.calculate_loan_payoff(
            loan=sample_loan,
            payoff_date="2025-01-01",
            prepayment_penalty_rate=2.0  # 2% penalty
        )

        # Penalty should be 2% of remaining balance
        expected_penalty = payoff["remaining_balance"] * 0.02
        assert abs(payoff["prepayment_penalty"] - expected_penalty) < 1.0

        # Total payoff should include penalty
        assert payoff["total_payoff_amount"] == payoff["remaining_balance"] + payoff["prepayment_penalty"]

    def test_payoff_interest_savings(self, loan_service, sample_loan):
        """Test that interest savings is calculated correctly"""
        sample_loan.monthly_payment = loan_service.calculate_monthly_payment(
            sample_loan.loan_amount,
            sample_loan.interest_rate,
            sample_loan.loan_term_years
        )

        payoff = loan_service.calculate_loan_payoff(
            loan=sample_loan,
            payoff_date="2025-01-01",
            prepayment_penalty_rate=0.0
        )

        # Interest savings should be positive (interest not paid on future payments)
        assert payoff["interest_savings"] > 0.0
