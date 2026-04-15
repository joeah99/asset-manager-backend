import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class ExtractedDocument(BaseModel):
    vendor_name: str = Field(description="Name of the vendor, seller, or lender")
    item_name: str = Field(description="Name or short description of the asset purchased, or the loan purpose")
    total_amount: float = Field(description="Total cost, purchase price, or loan amount")
    date: str = Field(description="Date of invoice or loan in YYYY-MM-DD format")
    type: str = Field(description="Must be exactly 'Asset' or 'Loan'")

def test_extraction(image_path="sample_invoice.png"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.")
        return

    client = genai.Client(api_key=api_key)
    
    print(f"Reading {image_path}...")
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except FileNotFoundError:
        print(f"Could not find {image_path}")
        return

    print("Sending to Gemini for JSON extraction...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                "Extract the key financial details from this document. If it's an invoice, treat it as an Asset. If it's a loan agreement, treat it as a Loan."
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedDocument,
            ),
        )
        
        print("\n--- Extracted JSON Data ---")
        # Pretty print the JSON output
        parsed = json.loads(response.text)
        print(json.dumps(parsed, indent=2))
        
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    test_extraction()
