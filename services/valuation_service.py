import json
from google import genai
from google.genai import types
import os

def generate_fmv_estimate(asset_data: dict) -> float:
    """
    Given asset data dict, send it to Gemini 2.5 Flash
    and return an estimated float FMV.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert appraiser. Estimate the current Fair Market Value (FMV) of the following asset based on these details:
    
    Type: {asset_data.get('asset_type', 'Unknown')}
    Manufacturer: {asset_data.get('manufacturer', 'Unknown')}
    Model: {asset_data.get('model', 'Unknown')}
    Model Year: {asset_data.get('model_year', 'Unknown')}
    Usage: {asset_data.get('usage', 0)} {asset_data.get('usage_unit', 'hours')}
    Condition: {asset_data.get('condition', 'Unknown')}
    Original Purchase Price: ${asset_data.get('purchase_price', 0)}
    
    Return ONLY a highly accurate numeric estimate as a float representing the dollar value. 
    Do not include symbols, commas, or text.
    """

    response = client.models.generate_content(
        model="models/gemini-3.1-flash-lite-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={"type": "object", "properties": {"estimated_fmv": {"type": "number"}}}
        )
    )

    try:
        data = json.loads(response.text)
        return float(data.get("estimated_fmv", 0.0))
    except Exception as e:
        print(f"Error in FMV service: {type(e).__name__}: {e}")
        if hasattr(response, 'text'):
             print(f"Response text: {response.text}")
        return 0.0
