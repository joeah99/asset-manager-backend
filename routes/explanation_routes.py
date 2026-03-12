from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from services.llm_explanation_service import generate_scenario_explanation

router = APIRouter()

class ExplanationRequest(BaseModel):
    scenario_data: Dict[str, Any]

@router.post("")
async def explain_scenario(req: ExplanationRequest):
    try:
        explanation = generate_scenario_explanation(req.scenario_data)
        return {"explanation": explanation}
    except ValueError as e:
        # e.g. API key missing
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Error in explain_scenario route: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI explanation.")
