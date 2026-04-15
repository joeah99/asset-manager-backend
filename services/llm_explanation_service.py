import os
from google import genai
from pydantic import BaseModel

class ExplanationRequest(BaseModel):
    scenario_data: dict

def generate_scenario_explanation(scenario_data: dict) -> str:
    """
    Generates a natural language explanation of the scenario results using Google Gemini.
    Strictly constrained to summarization without performing mathematical or tax calculations.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)
    
    # models/gemini-3.1-flash-lite-preview: Verified working with active quota.
    model = "models/gemini-3.1-flash-lite-preview"

    prompt = f"""
You are a financial summarizer. Your job is to summarize the provided financial scenario outcomes clearly and concisely.

CRITICAL CONSTRAINTS:
1. Do NOT perform any math or tax calculations. Use ONLY the numbers provided in the input data.
2. Explain the impact of the chosen depreciation methods purely based on the numbers provided.
3. Do NOT reference specific tax code years or make assumptions about tax rates unless they are explicitly provided in the input JSON.
4. Do NOT use markdown formatting (no asterisks for bolding, no hashtags for headers, etc.). Output pure PLAIN TEXT only.
5. You MUST include this EXACT disclaimer prominently at the bottom of your response:
"Disclaimer: This is an AI-generated summary of your scenario inputs and is not professional tax advice. Always consult a certified public accountant (CPA) or tax professional before making financial decisions."

Input Scenario Data:
{scenario_data}

Please provide a clear, professional summary of these results. Make it easy to read for an equipment owner or farmer. Use plain text dashes (-) for bullet points where appropriate for readability.
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=[prompt],
        )
        return response.text
    except Exception as e:
        print(f"Error generating explanation from Gemini: {type(e).__name__}: {e}")
        return "Error: Unable to generate a natural language explanation at this time. Please check your scenario details and try again. Our AI service might be temporarily busy or reaching its limit.\n\nDisclaimer: This is an AI-generated summary of your scenario inputs and is not professional tax advice. Always consult a certified public accountant (CPA) or tax professional before making financial decisions."
