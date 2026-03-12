from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import asyncpg
import os

from services.depreciation_schedule_service import DepreciationScheduleService

router = APIRouter()

from dotenv import load_dotenv
load_dotenv()

# Get DB URL from env
DATABASE_URL = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

# Pydantic Model
class PurchaseDTO(BaseModel):
    purchase_id: Optional[int] = None
    user_id: int
    asset_name: str
    asset_type: str
    manufacturer: str
    model: str
    model_year: str
    usage: Optional[float] = None
    usage_unit: Optional[str] = None
    cost: float
    depreciation_method: str
    business_use_percent: float
    in_service_month: str
    purchase_type: str = "REPLACEMENT"

@router.post("", response_model=PurchaseDTO)
async def create_purchase(purchase: PurchaseDTO):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Database URL not configured")
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        row = await conn.fetchrow("""
            INSERT INTO "Purchases" (
                user_id, asset_name, asset_type, manufacturer, model, model_year,
                usage, usage_unit, cost, depreciation_method,
                business_use_percent, in_service_month, "PurchaseType"
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING purchase_id
        """, purchase.user_id, purchase.asset_name, purchase.asset_type,
             purchase.manufacturer, purchase.model, purchase.model_year,
             purchase.usage, purchase.usage_unit, purchase.cost,
             purchase.depreciation_method, purchase.business_use_percent,
             purchase.in_service_month, purchase.purchase_type)
        
        purchase.purchase_id = row['purchase_id']
        return purchase
    except Exception as e:
        print(f"Error creating purchase: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@router.get("", response_model=List[PurchaseDTO])
async def get_purchases(user_id: int):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Database URL not configured")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Fetch all purchases for user
        rows = await conn.fetch("""
            SELECT * FROM "Purchases" WHERE user_id = $1 ORDER BY created_at DESC
        """, user_id)
        
        purchases = []
        for row in rows:
            purchases.append(PurchaseDTO(
                purchase_id=row['purchase_id'],
                user_id=row['user_id'],
                asset_name=row['asset_name'],
                asset_type=row['asset_type'],
                manufacturer=row['manufacturer'],
                model=row['model'],
                model_year=row['model_year'],
                usage=float(row['usage']) if row['usage'] is not None else None,
                usage_unit=row['usage_unit'],
                cost=float(row['cost']),
                depreciation_method=row['depreciation_method'],
                business_use_percent=float(row['business_use_percent']),
                in_service_month=row['in_service_month'],
                purchase_type=row['PurchaseType'] or "REPLACEMENT"
            ))
        return purchases
    except Exception as e:
        print(f"Error fetching purchases: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@router.delete("/{purchase_id}")
async def delete_purchase(purchase_id: int):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Database URL not configured")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute('DELETE FROM "Purchases" WHERE purchase_id = $1', purchase_id)
        return {"message": "Purchase deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@router.get("/{purchase_id}/depreciation-schedule")
async def get_purchase_depreciation_schedule(purchase_id: int):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Database URL not configured")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        row = await conn.fetchrow('SELECT * FROM "Purchases" WHERE purchase_id = $1', purchase_id)
        if not row:
            raise HTTPException(status_code=404, detail="Purchase not found")
            
        cost = float(row['cost'])
        business_use_percent = float(row['business_use_percent'])
        method = row['depreciation_method']
        in_service_month = row['in_service_month']  # format "YYYY-MM"
        
        try:
            year, month = map(int, in_service_month.split('-'))
            in_service_date = datetime(year, month, 1)
        except:
            in_service_date = datetime.now()
            
        schedule_service = DepreciationScheduleService()
        
        # Determine useful life from asset type if possible, assume 5 for most
        # simplified based on app assumptions
        useful_life = 5
        if row['asset_type'] in ['Tractor', 'Combine']:
            useful_life = 7
            
        schedule = schedule_service.generate_schedule(
            cost=cost,
            business_use_percent=business_use_percent,
            method=method,
            in_service_date=in_service_date,
            useful_life=useful_life
        )
        
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()
