import os
import json
import logging
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional

logger = logging.getLogger(__name__)

class ExtractedDocument(BaseModel):
    asset_type: Optional[str] = Field(default="Equipment", description="Type of asset. Options: 'Equipment', 'Vehicle', 'Tractor', 'Combine'. Guess based on item context.")
    manufacturer: Optional[str] = Field(default=None, description="Name of the manufacturer or vendor.")
    model: Optional[str] = Field(default=None, description="Model name of the asset, or generic item description if model isn't listed.")
    model_year: Optional[int] = Field(default=None, description="The manufacturing or model year of the asset as a 4-digit number.")
    usage: Optional[int] = Field(default=None, description="Usage amount (e.g., hours on a machine, miles on a vehicle).")
    purchase_price: Optional[float] = Field(default=None, description="The total purchase price or cost amount.")
    purchase_month: Optional[str] = Field(default=None, description="The 2-digit month of purchase (e.g., '01', '12').")
    purchase_year: Optional[str] = Field(default=None, description="The 4-digit year of purchase (e.g., '2024').")
    condition: Optional[str] = Field(default=None, description="Condition of the asset. Options: 'Excellent', 'Good', 'Fair', 'Poor'.")
    country: Optional[str] = Field(default="United States", description="Country of the transaction, e.g., 'United States', 'Canada', 'Mexico'.")
    zip_code: Optional[str] = Field(default=None, description="Zip code of the transaction or vendor location.")

class ExtractedLoanDocument(BaseModel):
    lender_name: Optional[str] = Field(default=None, description="Name of the lender or financial institution.")
    loan_name: Optional[str] = Field(default=None, description="Name or reference of the loan/account, like 'Equipment Finance', 'Truck Loan'.")
    loan_amount: Optional[float] = Field(default=None, description="The original loan or principal amount.")
    interest_rate: Optional[float] = Field(default=None, description="The interest rate as a percentage, e.g., 5.25 for 5.25%.")
    loan_term_years: Optional[int] = Field(default=None, description="The term of the loan converted/approximated to years.")
    loan_start_month: Optional[str] = Field(default=None, description="The 2-digit starting month, e.g., '01', '12'.")
    loan_start_year: Optional[str] = Field(default=None, description="The 4-digit starting year, e.g., '2024'.")

class DocumentExtractionService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY is not configured.")

        # models/gemini-3.1-flash-lite-preview: Verified working with active quota.
        self.model = "models/gemini-3.1-flash-lite-preview"

    async def extract_data_from_document(self, file_bytes: bytes, mime_type: str) -> dict:
        """
        Sends the document to Gemini and extracts structured JSON data.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured on the server.")

        prompt = (
            "You are a strict financial data extractor. "
            "Extract the key details from this equipment invoice, receipt, or document. "
            "Fill in as many fields as you can confidently determine from the text. "
            "If a field like 'Mileage' or 'Hours' is present, put it in 'usage'."
        )

        try:
            logger.info(f"Sending document ({len(file_bytes)} bytes) to Gemini ({self.model}) for extraction")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedDocument,
                    temperature=0.0 # Deterministic extraction
                ),
            )
            
            parsed_data = json.loads(response.text)
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error during document extraction: {e}")
            raise RuntimeError(f"Failed to extract document data: {str(e)}")

    async def extract_loan_data_from_document(self, file_bytes: bytes, mime_type: str) -> dict:
        """
        Sends the loan document to Gemini and extracts structured JSON data mapping to a Loan form.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured on the server.")

        prompt = (
            "You are a strict financial data extractor. "
            "Extract the key details from this loan document, promissory note, or finance agreement. "
            "Fill in as many fields as you can confidently determine from the text. "
        )

        try:
            logger.info(f"Sending loan document ({len(file_bytes)} bytes) to Gemini ({self.model}) for extraction")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedLoanDocument,
                    temperature=0.0 # Deterministic extraction
                ),
            )
            
            parsed_data = json.loads(response.text)
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error during loan document extraction: {e}")
            raise RuntimeError(f"Failed to extract loan document data: {str(e)}")
