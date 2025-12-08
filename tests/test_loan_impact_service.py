import pytest
from services.loan_impact_service import LoanImpactService
from services.loan_service import LoanInformationService
from models.loan_models import LoanInformationDTO


@pytest.fixture
def impact_service():
    """Fixture to create a LoanImpactService instance"""
    return LoanImpactService()


@pytest.fixture
def loan_service():
    """Fixture to create a LoanInformationService instance"""
    return LoanInformationService()


@pytest.fixture
def existing_loan(loan_service):
    """Fixture for an existing loan on an asset"""
    loan = LoanInformationDTO(
        loan_id=1,
        asset_id=100,
        user_id=1,
        lender_name="Old Bank",
        loan_amount=50000.0,
        interest_rate=6.0,
        loan_term_years=5,
        remaining_balance=50000.0,
        payment_frequency="Monthly",
        status="Active",
        loan_start_date="2024-01-01",
        loan_end_date="2029-01-01"
    )
    loan.monthly_payment = loan_service.calculate_monthly_payment(
        loan.loan_amount,
        loan.interest_rate,
        loan.loan_term_years
    )
    return loan


@pytest.fixture
def replacement_loan(loan_service):
    """Fixture for a loan on a replacement asset"""
    loan = LoanInformationDTO(
        loan_id=2,
        asset_id=200,
        user_id=1,
        lender_name="New Bank",
        loan_amount=60000.0,
        interest_rate=4.5,
        loan_term_years=5,
        remaining_balance=60000.0,
        payment_frequency="Monthly",
        status="Active",
        loan_start_date="2025-01-01",
        loan_end_date="2030-01-01"
    )
    loan.monthly_payment = loan_service.calculate_monthly_payment(
        loan.loan_amount,
        loan.interest_rate,
        loan.loan_term_years
    )
    return loan


class TestCalculateLiquidationImpact:
    """Tests for calculate_liquidation_impact method"""

    def test_liquidation_with_loan(self, impact_service, existing_loan):
        """Test liquidation impact calculation with an existing loan"""
        result = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=existing_loan,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        assert result["asset_sale_price"] == 60000.0
        assert result["transaction_fees"] == 1000.0
        assert result["loan_payoff"]["has_loan"] is True
        assert result["loan_payoff"]["remaining_balance"] > 0
        assert result["net_proceeds"] > 0
        assert result["gross_proceeds"] == 60000.0

    def test_liquidation_without_loan(self, impact_service):
        """Test liquidation impact calculation without a loan"""
        result = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=None,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        assert result["loan_payoff"]["has_loan"] is False
        assert result["loan_payoff"]["remaining_balance"] == 0.0
        assert result["loan_payoff"]["total_payoff_amount"] == 0.0
        assert result["net_proceeds"] == 59000.0  # 60000 - 1000 fees

    def test_liquidation_with_prepayment_penalty(self, impact_service, existing_loan):
        """Test liquidation with prepayment penalty"""
        result = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=existing_loan,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=2.0  # 2% penalty
        )

        assert result["loan_payoff"]["prepayment_penalty"] > 0
        assert result["loan_payoff"]["total_payoff_amount"] > result["loan_payoff"]["remaining_balance"]

    def test_liquidation_net_proceeds_calculation(self, impact_service, existing_loan):
        """Test that net proceeds are calculated correctly"""
        result = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=existing_loan,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        # Net proceeds = sale price - transaction fees - loan payoff
        expected_net = (
            result["asset_sale_price"] -
            result["transaction_fees"] -
            result["loan_payoff"]["total_payoff_amount"]
        )

        assert abs(result["net_proceeds"] - expected_net) < 0.01

    def test_liquidation_interest_savings(self, impact_service, existing_loan):
        """Test that interest savings is positive when paying off loan early"""
        result = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=existing_loan,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        # Should save interest by paying off early
        assert result["loan_payoff"]["interest_savings"] > 0


class TestCalculateReplacementImpact:
    """Tests for calculate_replacement_impact method"""

    def test_replacement_cash_required(self, impact_service, existing_loan, replacement_loan):
        """Test cash required calculation for replacement"""
        liquidation_impact = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=existing_loan,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        result = impact_service.calculate_replacement_impact(
            liquidation_impact=liquidation_impact,
            replacement_asset_price=70000.0,
            replacement_loan=replacement_loan,
            existing_loan=existing_loan
        )

        assert "cash_required" in result
        assert "down_payment_required" in result
        assert result["replacement_asset_price"] == 70000.0

    def test_replacement_monthly_payment_comparison(self, impact_service, existing_loan, replacement_loan):
        """Test monthly payment comparison calculation"""
        liquidation_impact = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=existing_loan,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        result = impact_service.calculate_replacement_impact(
            liquidation_impact=liquidation_impact,
            replacement_asset_price=70000.0,
            replacement_loan=replacement_loan,
            existing_loan=existing_loan
        )

        assert "monthly_payment_comparison" in result
        assert result["monthly_payment_comparison"]["old_monthly_payment"] == existing_loan.monthly_payment
        assert result["monthly_payment_comparison"]["new_monthly_payment"] == replacement_loan.monthly_payment
        assert "monthly_change" in result["monthly_payment_comparison"]

    def test_replacement_with_no_new_loan(self, impact_service, existing_loan):
        """Test replacement scenario where replacement is paid in cash"""
        liquidation_impact = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=existing_loan,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        result = impact_service.calculate_replacement_impact(
            liquidation_impact=liquidation_impact,
            replacement_asset_price=40000.0,
            replacement_loan=None,  # Paying cash
            existing_loan=existing_loan
        )

        assert result["monthly_payment_comparison"]["new_monthly_payment"] == 0.0
        assert result["monthly_payment_comparison"]["monthly_change"] < 0  # Payment eliminated

    def test_replacement_interest_cost_comparison(self, impact_service, existing_loan, replacement_loan):
        """Test interest cost comparison calculation"""
        liquidation_impact = impact_service.calculate_liquidation_impact(
            asset_sale_price=60000.0,
            existing_loan=existing_loan,
            liquidation_date="2025-01-01",
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        result = impact_service.calculate_replacement_impact(
            liquidation_impact=liquidation_impact,
            replacement_asset_price=70000.0,
            replacement_loan=replacement_loan,
            existing_loan=existing_loan
        )

        assert "interest_cost_comparison" in result
        assert "total_interest_old_loan" in result["interest_cost_comparison"]
        assert "total_interest_new_loan" in result["interest_cost_comparison"]
        assert "interest_cost_change" in result["interest_cost_comparison"]


class TestCalculateTotalScenarioImpact:
    """Tests for calculate_total_scenario_impact method"""

    def test_complete_scenario_analysis(self, impact_service, existing_loan, replacement_loan):
        """Test complete scenario analysis with all components"""
        result = impact_service.calculate_total_scenario_impact(
            asset_sale_price=60000.0,
            liquidation_date="2025-01-01",
            existing_loan=existing_loan,
            replacement_asset_price=70000.0,
            replacement_loan=replacement_loan,
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        # Check all major sections exist
        assert "scenario_summary" in result
        assert "liquidation_details" in result
        assert "replacement_details" in result
        assert "recommendation" in result

    def test_scenario_summary_calculations(self, impact_service, existing_loan, replacement_loan):
        """Test that scenario summary has all required fields"""
        result = impact_service.calculate_total_scenario_impact(
            asset_sale_price=60000.0,
            liquidation_date="2025-01-01",
            existing_loan=existing_loan,
            replacement_asset_price=70000.0,
            replacement_loan=replacement_loan,
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        summary = result["scenario_summary"]
        assert "net_cash_impact" in summary
        assert "monthly_obligation_change" in summary
        assert "annual_obligation_change" in summary
        assert "interest_savings_from_payoff" in summary
        assert "total_interest_cost_change" in summary

    def test_recommendation_generation(self, impact_service, existing_loan, replacement_loan):
        """Test that recommendation is generated"""
        result = impact_service.calculate_total_scenario_impact(
            asset_sale_price=60000.0,
            liquidation_date="2025-01-01",
            existing_loan=existing_loan,
            replacement_asset_price=70000.0,
            replacement_loan=replacement_loan,
            transaction_fees=1000.0,
            prepayment_penalty_rate=0.0
        )

        recommendation = result["recommendation"]
        assert "recommendation" in recommendation
        assert "positive_score" in recommendation
        assert "negative_score" in recommendation
        assert "key_factors" in recommendation
        assert isinstance(recommendation["key_factors"], list)
        assert len(recommendation["key_factors"]) > 0

    def test_favorable_scenario(self, impact_service, existing_loan):
        """Test scenario that should be favorable (selling high, buying low with no loan)"""
        result = impact_service.calculate_total_scenario_impact(
            asset_sale_price=80000.0,  # High sale price
            liquidation_date="2025-01-01",
            existing_loan=existing_loan,
            replacement_asset_price=40000.0,  # Low replacement price
            replacement_loan=None,  # No new loan
            transaction_fees=500.0,
            prepayment_penalty_rate=0.0
        )

        recommendation = result["recommendation"]
        # Should be favorable with positive score
        assert recommendation["positive_score"] >= recommendation["negative_score"]

    def test_unfavorable_scenario(self, impact_service, replacement_loan):
        """Test scenario that should be unfavorable (selling low, buying high with loan)"""
        high_interest_loan = LoanInformationDTO(
            loan_id=3,
            asset_id=300,
            user_id=1,
            lender_name="Expensive Bank",
            loan_amount=90000.0,
            interest_rate=12.0,  # High interest rate
            loan_term_years=5,
            remaining_balance=90000.0,
            payment_frequency="Monthly",
            status="Active",
            loan_start_date="2025-01-01",
            loan_end_date="2030-01-01"
        )

        from services.loan_service import LoanInformationService
        service = LoanInformationService()
        high_interest_loan.monthly_payment = service.calculate_monthly_payment(
            high_interest_loan.loan_amount,
            high_interest_loan.interest_rate,
            high_interest_loan.loan_term_years
        )

        result = impact_service.calculate_total_scenario_impact(
            asset_sale_price=40000.0,  # Low sale price
            liquidation_date="2025-01-01",
            existing_loan=None,  # No existing loan to pay off
            replacement_asset_price=100000.0,  # Expensive replacement
            replacement_loan=high_interest_loan,  # High interest loan
            transaction_fees=2000.0,
            prepayment_penalty_rate=0.0
        )

        # Should have some negative factors
        recommendation = result["recommendation"]
        assert recommendation["negative_score"] > 0
