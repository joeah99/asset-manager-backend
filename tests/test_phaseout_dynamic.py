
import pytest
from services.tax_policy_service import TaxPolicyService

def test_dynamic_phaseout_threshold_calculation():
    """
    Verify that providing an override limit correctly adjusts the phase-out threshold
    to maintain the standard 'gap' between Limit and Threshold.
    """
    service = TaxPolicyService()
    year = 2026
    
    # Standard 2026 values
    policy = service.get_policy_for_year(year)
    standard_limit = 2_560_000
    standard_threshold = 4_090_000
    gap = standard_threshold - standard_limit # 1,530,000
    
    assert policy.section_179_limit == standard_limit
    assert policy.section_179_phaseout_threshold == standard_threshold
    
    # Case 1: Override Limit to 100,000
    # Expected Threshold = 100,000 + 1,530,000 = 1,630,000
    override_limit = 100_000.0
    expected_threshold = override_limit + gap
    
    # Sub-test A: Purchases BELOW dynamic threshold
    # Purchase = 1,600,000 (Below 1.63M)
    # Deduction should be full override limit (100,000)
    purchases_a = 1_600_000
    result_a = service.calculate_section_179_limit_with_phaseout(
        purchases_a, year, override_limit
    )
    assert result_a == 100_000.0
    
    # Sub-test B: Purchases ABOVE dynamic threshold
    # Purchase = 1,680,000 (50,000 above 1.63M)
    # Deduction should be reduced by 50,000 -> 50,000 remaining
    purchases_b = 1_680_000
    result_b = service.calculate_section_179_limit_with_phaseout(
        purchases_b, year, override_limit
    )
    assert result_b == 50_000.0
    
    # Sub-test C: Purchases WAY ABOVE (Full phaseout)
    # Purchase = 1,730,000 (100,000 above 1.63M)
    # Deduction should be 0
    purchases_c = 1_730_000
    result_c = service.calculate_section_179_limit_with_phaseout(
        purchases_c, year, override_limit
    )
    assert result_c == 0.0

def test_legacy_behavior_preserved():
    """Verify that without override, standard rules apply."""
    service = TaxPolicyService()
    year = 2026
    
    # Just above standard threshold (4.09M) by 100k
    purchases = 4_190_000
    
    # Standard Limit: 2.56M -> Reduced to 2.46M
    result = service.calculate_section_179_limit_with_phaseout(
        purchases, year, override_limit=None
    )
    assert result == 2_460_000.0
