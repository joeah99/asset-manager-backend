import httpx
import asyncio

async def test_purchases_endpoint():
    """Test the purchases endpoint"""
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: GET /purchases
    print("Test 1: GET /purchases?user_id=5")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/purchases?user_id=5")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Test 2: POST /purchases
    print("Test 2: POST /purchases")
    test_purchase = {
        "user_id": 5,
        "asset_name": "2023 Test Equipment",
        "asset_type": "Equipment",
        "manufacturer": "Test Co",
        "model": "X100",
        "model_year": "2023",
        "usage": 1000,
        "usage_unit": "hours",
        "cost": 50000,
        "depreciation_method": "AUTO",
        "business_use_percent": 100,
        "in_service_month": "2026-01",
        "purchase_type": "REPLACEMENT"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/purchases", json=test_purchase)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Test 3: Check /docs
    print("Test 3: GET /docs (check if server is running)")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/docs")
            print(f"Status: {response.status_code}")
            print(f"Has /purchases in docs: {'/purchases' in response.text}")
            print()
    except Exception as e:
        print(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_purchases_endpoint())
