from fastapi import APIRouter
from pydantic import BaseModel
import logging
from services.valuation_service import generate_fmv_estimate

router = APIRouter()
logger = logging.getLogger(__name__)

class FmvRequest(BaseModel):
    asset_id: int
    asset_type: str
    manufacturer: str
    model: str
    model_year: str
    usage: float
    usage_unit: str
    condition: str
    purchase_price: float

@router.post("/estimate-fmv")
async def estimate_fmv(request: FmvRequest):
    try:
        data = request.model_dump()
        fmv = generate_fmv_estimate(data)
        return {"estimated_fmv": fmv}
    except Exception as e:
        logger.error(f"Error estimating FMV via AI: {e}")
        return {"estimated_fmv": 0.0}
