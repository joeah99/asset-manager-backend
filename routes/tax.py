from fastapi import APIRouter, HTTPException
from services.dotnet_client import dotnet_api

router = APIRouter()

@router.get("/tax/{asset_id}")
async def get_tax(asset_id: int):
    try:
        data = await dotnet_api.get("/api/tax/calculations", params={"assetId": asset_id})
        return {"source": "dotnet-backend", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling .NET backend: {e}")
