
import pytest
from datetime import datetime
from services.depreciation_calculation_service import DepreciationCalculationService
from services.tax_policy_service import TaxPolicyService

@pytest.fixture
def service():
    return DepreciationCalculationService()

def test_bonus_depreciation_2026_is_100_percent(service):
    """Verify that bonus depreciation for 2026 is 100% as requested."""
    # 2026 date
    in_service_date = datetime(2026, 6, 15)
    cost = 10000.0
    business_use = 100.0
    
    result = service.calculate_bonus_depreciation(
        asset_name="Test Asset",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date
    )
    
    # Expect 100% deduction
    assert result.bonus_depreciation == 10000.0
    assert result.total_first_year_deduction == 10000.0
    assert result.remaining_basis == 0.0

def test_business_use_impacts_basis_bonus(service):
    """Verify business use applies correctly for Bonus Depreciation."""
    in_service_date = datetime(2026, 6, 15)
    cost = 10000.0
    business_use = 80.0  # 80% business use
    
    # Depreciable basis should be 8000
    # Bonus (100%) should be 8000
    
    result = service.calculate_bonus_depreciation(
        asset_name="Test Asset",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date
    )
    
    assert result.depreciable_basis == 8000.0
    assert result.bonus_depreciation == 8000.0
    assert result.total_first_year_deduction == 8000.0

def test_business_use_impacts_basis_section_179(service):
    """Verify business use applies correctly for Section 179."""
    in_service_date = datetime(2026, 6, 15)
    cost = 10000.0
    business_use = 75.0  # 75% business use
    
    # Depreciable basis should be 7500
    
    result = service.calculate_section_179(
        asset_name="Test Asset",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date,
        section_179_available=50000.0
    )
    
    assert result.depreciable_basis == 7500.0
    assert result.section_179_deduction == 7500.0
    assert result.total_first_year_deduction == 7500.0

def test_business_use_impacts_basis_macrs(service):
    """Verify business use applies correctly for MACRS."""
    in_service_date = datetime(2026, 1, 1) # Jan 1 to avoid mid-quarter complexity if any (though logic uses half-year implied by tables usually but here just rate lookup)
    cost = 10000.0
    business_use = 60.0  # Updated to 60.0 to stay in GDS (avoid forced ADS)
    
    # Depreciable basis = 6000
    # MACRS 5-year GDS year 1 is 20%
    # Deduction = 6000 * 0.20 = 1200
    
    result = service.calculate_macrs_gds(
        asset_name="Test Asset",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date,
        useful_life=5
    )
    
    assert result.depreciable_basis == 6000.0
    assert result.macrs_first_year == 1200.0 
    assert result.total_first_year_deduction == 1200.0

def test_optimal_method_stacking_2026(service):
    """Verify optimal method stacking with 2026 rules (100% Bonus)."""
    in_service_date = datetime(2026, 6, 15)
    cost = 100000.0
    business_use = 100.0
    
    # With 100% bonus, even if we don't use 179, Bonus should take it all.
    # But usually 179 is applied first.
    
    # Scenario 1: No 179 available
    result = service.calculate_optimal_method(
        asset_name="Test Asset",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date,
        section_179_available=0.0
    )
    
    assert result.section_179_deduction == 0.0
    assert result.bonus_depreciation == 100000.0
    assert result.macrs_first_year == 0.0
    assert result.total_first_year_deduction == 100000.0

    # Scenario 2: 179 available
    result_179 = service.calculate_optimal_method(
        asset_name="Test Asset",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date,
        section_179_available=50000.0
    )
    
    # Should take 50k 179, then 50k bonus
    assert result_179.section_179_deduction == 50000.0
    assert result_179.bonus_depreciation == 50000.0
    assert result_179.macrs_first_year == 0.0
    assert result_179.total_first_year_deduction == 100000.0

def test_section_179_limit_2026(service):
    """Verify Section 179 limit for 2026 is 2,560,000."""
    policy = TaxPolicyService().get_policy_for_year(2026)
    assert policy.section_179_limit == 2560000

def test_auto_max_strict_order_2026(service):
    """
    Verify Auto-Max strictly follows: Section 179 -> Bonus -> MACRS.
    Using a large asset cost to trigger all layers.
    """
    in_service_date = datetime(2026, 6, 15)
    cost = 4_000_000.0 # 4M asset
    business_use = 100.0
    
    # 2026 Constants
    # Section 179 Limit: 2,560,000
    # Bonus: 100%
    
    # Assume we have full 179 available
    section_179_available = 2_560_000.0
    
    # Expected Flow:
    # 1. Section 179: Takes 2,560,000 (Max limit) -> Remaining Basis: 1,440,000
    # 2. Bonus: Takes 100% of 1,440,000 -> Remaining Basis: 0
    # 3. MACRS: Takes 0 (No basis left)
    
    result = service.calculate_optimal_method(
        asset_name="Large Asset",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date,
        section_179_available=section_179_available
    )
    
    assert result.section_179_deduction == 2560000.0
    assert result.bonus_depreciation == 1440000.0
    assert result.macrs_first_year == 0.0
    assert result.total_first_year_deduction == 4000000.0

def test_auto_max_strict_order_limited_bonus(service):
    """
    Verify Auto-Max with limited bonus to ensure MACRS picks up the rest.
    Example: Override Bonus to 50% just to prove the chain works.
    """
    in_service_date = datetime(2026, 6, 15)
    cost = 100_000.0
    business_use = 100.0
    section_179_available = 40_000.0 # Restrict 179
    
    # Overriding Bonus to 50% manually to test flow
    override_bonus = 50
    
    # Expected Flow:
    # 1. Section 179: Takes 40,000 -> Remaining: 60,000
    # 2. Bonus: Takes 50% of 60,000 = 30,000 -> Remaining: 30,000
    # 3. MACRS (5yr GDS): Takes 20% of 30,000 = 6,000 -> Remaining: 24,000
    
    result = service.calculate_optimal_method(
        asset_name="Test Chain",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date,
        section_179_available=section_179_available,
        override_bonus_percent=override_bonus
    )
    
    assert result.section_179_deduction == 40000.0
    assert result.bonus_depreciation == 30000.0
    assert result.macrs_first_year == 6000.0
    assert result.total_first_year_deduction == 76000.0

def test_section_179_phaseout_2026(service):
    """
    Verify Section 179 phase-out logic for 2026.
    Threshold: 4,090,000
    Limit: 2,560,000
    """
    in_service_date = datetime(2026, 6, 15)
    
    # Case 1: Just below threshold - Full limit available
    # Cost: 4,000,000
    # Expected Limit: 2,560,000
    limit_1 = TaxPolicyService().calculate_section_179_limit_with_phaseout(4_000_000, 2026)
    assert limit_1 == 2_560_000
    
    # Case 2: Above threshold by 100k
    # Cost: 4,190,000
    # Excess: 100,000
    # Reduced Limit: 2,560,000 - 100,000 = 2,460,000
    limit_2 = TaxPolicyService().calculate_section_179_limit_with_phaseout(4_190_000, 2026)
    assert limit_2 == 2_460_000
    
    # Case 3: Fully phased out
    # Cost: 4,090,000 + 2,560,000 = 6,650,000
    limit_3 = TaxPolicyService().calculate_section_179_limit_with_phaseout(6_700_000, 2026)
    assert limit_3 == 0

def test_business_use_low_threshold_compliance(service):
    """
    Verify strict 50% Business Use rule.
    If <= 50%:
    1. No Bonus
    2. No Section 179
    3. Forced ADS
    """
    in_service_date = datetime(2026, 6, 15)
    cost = 10_000.0
    business_use_50 = 50.0 # Exactly 50% - should fail
    
    
    # 1. Test Auto-Max (should switch to ADS)
    result = service.calculate_optimal_method(
        asset_name="Low Biz Use Asset",
        cost=cost,
        business_use_percent=business_use_50,
        in_service_date=in_service_date,
        section_179_available=100_000.0
    )
    
    
    assert result.method_used == "First_Year_Maximized"
    assert result.section_179_deduction == 0.0
    assert result.bonus_depreciation == 0.0
    
    # Calculate expected ADS
    # Basis: 50% of 10,000 = 5,000
    # ADS 5-yr (really 6 years) -> 1/5 * 0.5 = 10%
    # Deduction = 5,000 * 0.10 = 500
    assert result.macrs_first_year == 500.0
    assert result.total_first_year_deduction == 500.0
    
    # 2. Test Section 179 Direct Call
    res_179 = service.calculate_section_179(
        "Test 179", cost, business_use_50, in_service_date, 100000
    )
    assert res_179.section_179_deduction == 0.0
    assert "not available" in res_179.notes[0]

    # 3. Test Bonus Direct Call
    res_bonus = service.calculate_bonus_depreciation(
        "Test Bonus", cost, business_use_50, in_service_date
    )
    assert "not available" in res_bonus.notes[0]

def test_user_complex_scenario(service):
    """
    Regression test for user-provided scenario:
    - Cost: 500,000
    - Business Use: 60% (Basis = 300,000)
    - 179 Limit: 100,000
    - Bonus: 50%
    
    Expected:
    1. 179: Takes 100,000 (Limit). Rem Basis: 200,000.
    2. Bonus: 50% of 200,000 = 100,000. Rem Basis: 100,000.
    3. MACRS: 20% (5yr GDS) of 100,000 = 20,000.
    Total: 220,000.
    """
    in_service_date = datetime(2026, 6, 15)
    cost = 500_000.0
    business_use = 60.0
    section_179_limit_remaining = 100_000.0
    override_bonus = 50
    
    result = service.calculate_optimal_method(
        asset_name="User Scenario",
        cost=cost,
        business_use_percent=business_use,
        in_service_date=in_service_date,
        section_179_available=section_179_limit_remaining,
        override_bonus_percent=override_bonus
    )
    
    # Validation
    assert result.depreciable_basis == 300_000.0
    assert result.section_179_deduction == 100_000.0
    assert result.bonus_depreciation == 100_000.0
    assert result.macrs_first_year == 20_000.0
    assert result.total_first_year_deduction == 220_000.0

