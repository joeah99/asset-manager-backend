import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class DotNetAPIClient:
    def __init__(self):
        self.base_url = os.getenv("DOTNET_API_BASE", "https://localhost:5001")
        self.client = httpx.AsyncClient(verify=False, timeout=10)

    async def get(self, endpoint: str, params: dict = None):
        """Send a GET request to the .NET API."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def post(self, endpoint: str, data: dict = None, json: dict = None):
        """Send a POST request to the .NET API."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = await self.client.post(url, data=data, json=json)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()

dotnet_api = DotNetAPIClient()
