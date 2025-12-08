import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app

@pytest.fixture
def mock_dotnet_api():
    """Mock the dotnet_api service"""
    with patch('routes.tax.dotnet_api') as mock:
        yield mock

@pytest.mark.asyncio
async def test_get_tax_success(mock_dotnet_api):
    """Test successful tax retrieval"""
    # Note: This test requires the tax route to be registered in main.py
    # If the route is not registered, these tests will need to be updated
    mock_dotnet_api.get = AsyncMock(return_value={"tax": 1000, "asset_id": 1})
    
    # Test the route directly if it exists
    # The actual route path depends on how it's registered in main.py
    # For now, we'll test the route logic directly
    from routes import tax
    
    # Mock the route function
    with patch('routes.tax.dotnet_api') as mock:
        mock.get = AsyncMock(return_value={"tax": 1000, "asset_id": 1})
        result = await tax.get_tax(1)
        assert "source" in result
        assert "data" in result

@pytest.mark.asyncio
async def test_get_tax_error_handling(mock_dotnet_api):
    """Test tax endpoint error handling"""
    from routes import tax
    from fastapi import HTTPException
    
    with patch('routes.tax.dotnet_api') as mock:
        mock.get = AsyncMock(side_effect=Exception("Connection error"))
        with pytest.raises(HTTPException) as exc_info:
            await tax.get_tax(1)
        assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_get_tax_with_valid_asset_id(mock_dotnet_api):
    """Test tax endpoint with valid asset ID"""
    from routes import tax
    
    with patch('routes.tax.dotnet_api') as mock:
        mock.get = AsyncMock(return_value={"tax": 500, "asset_id": 1})
        result = await tax.get_tax(1)
        assert result["data"]["asset_id"] == 1

@pytest.mark.asyncio
async def test_get_tax_with_invalid_asset_id(mock_dotnet_api):
    """Test tax endpoint with invalid asset ID"""
    from routes import tax
    from fastapi import HTTPException
    
    with patch('routes.tax.dotnet_api') as mock:
        mock.get = AsyncMock(side_effect=Exception("Asset not found"))
        with pytest.raises(HTTPException) as exc_info:
            await tax.get_tax(999)
        assert exc_info.value.status_code == 500

