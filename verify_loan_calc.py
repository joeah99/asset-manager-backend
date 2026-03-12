import requests
import json
import time

def verify_loan_integration():
    """
    Verify that the scenario calculation correctly includes annual debt service
    from the user's active loans.
    """
    base_url = "http://127.0.0.1:8000"
    user_id = 5  # The user we've been working with
    
    print("=== VERIFYING LOAN INTEGRATION ===")
    
    # Step 1: Fetch Loans to see what we expect
    print(f"\n1. Fetching active loans for User {user_id}...")
    try:
        loans_response = requests.get(f"{base_url}/loans", params={"user_id": user_id})
        if loans_response.status_code != 200:
            print(f"❌ Failed to fetch loans: {loans_response.status_code}")
            return
            
        loans = loans_response.json()
        active_loans = [l for l in loans if l.get('status', '').lower() == 'active']
        
        expected_annual_debt = sum(l['monthly_payment'] * 12 for l in active_loans)
        
        print(f"   Found {len(active_loans)} active loans.")
        for loan in active_loans:
            print(f"   - {loan['loan_name']}: ${loan['monthly_payment']}/mo x 12 = ${loan['monthly_payment']*12:,.2f}/yr")
        
        print(f"   Expected Total Annual Debt Service: ${expected_annual_debt:,.2f}")
        
    except Exception as e:
        print(f"❌ Error fetching loans: {e}")
        return

    # Step 2: Trigger Scenario Calculation
    print(f"\n2. Triggering Scenario Calculation...")
    
    # Minimal payload required for calculation
    payload = {
        "userId": user_id,
        "assetsToSell": [], # Empty is fine, we just need the global loan calc
        "replacementAssets": [],
        "marginalTaxRate": 0.24,
        "capitalGainsRate": 0.15
    }
    
    try:
        # Time the request
        start_time = time.time()
        response = requests.post(f"{base_url}/scenarios/calculate", json=payload)
        duration = time.time() - start_time
        
        print(f"   Request took {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            actual_debt_service = data.get('totalAnnualDebtService', 0)
            
            print(f"   API Response 'totalAnnualDebtService': ${actual_debt_service:,.2f}")
            
            # Step 3: Compare
            print(f"\n3. Verification Results:")
            if abs(actual_debt_service - expected_annual_debt) < 0.01:
                if actual_debt_service > 0:
                    print("   SUCCESS: API returned correct non-zero debt service!")
                else:
                    print("   WARNING: Debt service is 0. Check if user has active loans.")
            else:
                print(f"   FAILURE: Mismatch! Expected ${expected_annual_debt:,.2f}, got ${actual_debt_service:,.2f}")
                
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error calling scenario API: {e}")

if __name__ == "__main__":
    verify_loan_integration()
