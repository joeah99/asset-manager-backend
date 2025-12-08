import httpx
from typing import Optional
from urllib.parse import quote
from models.valuation_models import EquipmentValuationDTO, VehicleValuationDTO
import os
from dotenv import load_dotenv

load_dotenv()


class AssetValuationService:
    """
    Service for fetching asset valuations from external APIs
    (equivalent to C# AssetValuationService)

    Uses:
    - EquipmentWatch API for equipment valuations
    - PriceDigest API for vehicle valuations
    """

    EQUIPMENT_WATCH_TAXONOMY_URL = "https://equipmentwatchapi.com/v1/taxonomy/models"
    EQUIPMENT_WATCH_VALUE_URL = "https://equipmentwatchapi.com/v1/values/value"
    PRICE_DIGEST_TAXONOMY_URL = "https://pricedigestsapi.com/v1/taxonomy/configurations/"
    PRICE_DIGEST_VALUE_URL = "https://pricedigestsapi.com/v1/values/value/"

    def __init__(self, equipment_api_key: str = None, vehicle_api_key: str = None):
        self.equipment_api_key = equipment_api_key or os.getenv("EQUIPMENT_WATCH_API_KEY")
        self.vehicle_api_key = vehicle_api_key or os.getenv("PRICE_DIGEST_API_KEY")

    def _build_taxonomy_api_url(self, base_url: str, manufacturer: str, model: str, model_year: str) -> str:
        """Build taxonomy API URL with query parameters"""
        return f"{base_url}?model={quote(model)}&manufacturer={quote(manufacturer)}&modelYear={quote(model_year)}"

    def _build_value_api_url(
        self,
        base_url: str,
        model_id: str,
        year: str,
        usage: str,
        condition: str,
        country: str,
        region: str
    ) -> str:
        """Build equipment value API URL"""
        return f"{base_url}?modelId={quote(model_id)}&year={year}&usage={usage}&condition={quote(condition)}&country={quote(country)}&region={quote(region)}"

    def _build_vehicle_value_api_url(
        self,
        base_url: str,
        configuration_id: str,
        usage: str,
        condition: str,
        country: str,
        state: str
    ) -> str:
        """Build vehicle value API URL"""
        return f"{base_url}?configurationId={quote(configuration_id)}&usage={usage}&condition={quote(condition)}&country={quote(country)}&state={quote(state)}"

    def _get_api_key(self, asset_type: str) -> str:
        """Get appropriate API key based on asset type"""
        return self.equipment_api_key if asset_type == "Equipment" else self.vehicle_api_key

    async def get_equipment_valuation_async(
        self,
        manufacturer: str,
        model: str,
        model_year: str,
        usage: str,
        condition: str,
        country: str,
        region: str
    ) -> EquipmentValuationDTO:
        """
        Get equipment valuation from EquipmentWatch API

        Args:
            manufacturer: Equipment manufacturer
            model: Equipment model
            model_year: Model year
            usage: Usage hours
            condition: Equipment condition
            country: Country code
            region: State/region code

        Returns:
            Equipment valuation data

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If no valid model ID found
        """
        taxonomy_url = self._build_taxonomy_api_url(
            self.EQUIPMENT_WATCH_TAXONOMY_URL,
            manufacturer,
            model,
            model_year
        )
        api_key = self._get_api_key("Equipment")

        async with httpx.AsyncClient() as client:
            # Fetch taxonomy data to get model ID
            headers = {"x-api-key": api_key}
            taxonomy_response = await client.get(taxonomy_url, headers=headers)
            taxonomy_response.raise_for_status()

            taxonomy_data = taxonomy_response.json()

            # Extract model ID from response
            model_id = None

            if isinstance(taxonomy_data, dict):
                model_id = taxonomy_data.get("modelId")
            elif isinstance(taxonomy_data, list):
                for item in taxonomy_data:
                    if "modelId" in item:
                        model_id = str(item["modelId"])
                        break

            if not model_id:
                raise ValueError("No valid model ID found in taxonomy data")

            # Fetch valuation data
            valuation_url = self._build_value_api_url(
                self.EQUIPMENT_WATCH_VALUE_URL,
                str(model_id),
                model_year,
                usage,
                condition,
                country,
                region
            )

            valuation_response = await client.get(valuation_url, headers=headers)
            valuation_response.raise_for_status()

            valuation_data = valuation_response.json()

            # Parse into DTO
            return EquipmentValuationDTO(**valuation_data)

    async def get_vehicle_valuation_async(
        self,
        manufacturer: str,
        model: str,
        model_year: str,
        usage: str,
        condition: str,
        country: str,
        region: str
    ) -> VehicleValuationDTO:
        """
        Get vehicle valuation from PriceDigest API

        Args:
            manufacturer: Vehicle manufacturer
            model: Vehicle model
            model_year: Model year
            usage: Mileage/usage
            condition: Vehicle condition
            country: Country code
            region: State/region code

        Returns:
            Vehicle valuation data

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If no valid configuration ID found
        """
        taxonomy_url = self._build_taxonomy_api_url(
            self.PRICE_DIGEST_TAXONOMY_URL,
            manufacturer,
            model,
            model_year
        )
        api_key = self._get_api_key("Vehicle")

        async with httpx.AsyncClient() as client:
            # Fetch taxonomy data to get configuration ID
            headers = {"x-api-key": api_key}
            taxonomy_response = await client.get(taxonomy_url, headers=headers)
            taxonomy_response.raise_for_status()

            taxonomy_data = taxonomy_response.json()

            # Extract configuration ID from response
            configuration_id = None

            if isinstance(taxonomy_data, list):
                for item in taxonomy_data:
                    if "configurationId" in item:
                        configuration_id = str(item["configurationId"])
                        break

            if not configuration_id:
                raise ValueError("No valid configuration ID found in taxonomy data")

            # Fetch valuation data
            valuation_url = self._build_vehicle_value_api_url(
                self.PRICE_DIGEST_VALUE_URL,
                configuration_id,
                usage,
                condition,
                country,
                region
            )

            valuation_response = await client.get(valuation_url, headers=headers)
            valuation_response.raise_for_status()

            valuation_data = valuation_response.json()

            # Parse into DTO
            return VehicleValuationDTO(**valuation_data)
