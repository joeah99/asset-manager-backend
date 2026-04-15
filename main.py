from dotenv import load_dotenv
import os
import logging
from contextlib import asynccontextmanager

# Load .env values immediately
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import loan_routes, assets, scenarios, auth, purchase_routes

# Setup logging — stdout only (required for Render/cloud hosts)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

db_url = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
DOTNET_API_BASE = os.getenv("DOTNET_API_BASE")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Initialize DB tables, seed tax policies, and warm the policy cache.
    Shutdown: No-op.
    """
    logger.info("Starting up — initializing database and loading tax policies...")
    
    try:
        # 1. Ensure all tables exist (including TaxPolicyYear)
        from init_db import init_db
        await init_db()
        
        # 2. Seed default tax policies if table is empty
        from migrations.seed_tax_policies import seed_tax_policies
        await seed_tax_policies()
        
        # 3. Load policies from DB into the in-memory cache
        from routes.scenarios import tax_policy_service
        await tax_policy_service.load_policies_from_db()
        
        logger.info("Startup complete — tax policies loaded from database.")
    except Exception as e:
        logger.error(f"Startup warning — using fallback tax policies: {e}")
        # App still starts — fallback policies are always available
    
    yield  # App is running
    
    # Shutdown (nothing to clean up)
    logger.info("Shutting down.")


app = FastAPI(title="Python Backend (Asset Manager Stage 2)", lifespan=lifespan)

# Register routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(assets.router, prefix="", tags=["Assets"])
app.include_router(loan_routes.router, prefix="", tags=["LoanInformation"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
app.include_router(purchase_routes.router, prefix="/purchases", tags=["Purchases"])

from routes import explanation_routes, document_routes, valuation
app.include_router(explanation_routes.router, prefix="/scenarios/explain", tags=["AI Explanation"])
app.include_router(document_routes.router, prefix="", tags=["Document Extraction"])
app.include_router(valuation.router, prefix="/valuation", tags=["Valuation"])

# Allow your React frontend to call this API
origins = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
