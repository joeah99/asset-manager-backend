from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import commodities, loans, auth, assets, valuations, scenarios
from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.monthly_asset_valuation_job import run_monthly_valuation_job
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env values
load_dotenv()

app = FastAPI(title="Python Backend (Asset Manager Stage 2)")

# Initialize scheduler
scheduler = BackgroundScheduler()

# Add monthly valuation job - runs at 1 AM on the first day of every month
scheduler.add_job(
    run_monthly_valuation_job,
    CronTrigger(day=1, hour=1, minute=0),
    id='monthly_asset_valuation',
    name='Monthly Asset Valuation Update',
    replace_existing=True
)

# Start scheduler
scheduler.start()
logger.info("Scheduler started - Monthly asset valuation job scheduled for 1st of each month at 1 AM")

db_url = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
DOTNET_API_BASE = os.getenv("DOTNET_API_BASE")

# Register routes
app.include_router(auth.router, prefix="", tags=["Account"])
app.include_router(assets.router, prefix="", tags=["Assets"])
app.include_router(loans.router, prefix="", tags=["LoanInformation"])
app.include_router(valuations.router, prefix="/Valuation", tags=["Valuation"])
app.include_router(commodities.router, prefix="/commodities", tags=["Commodities"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
allowed_origins.append("https://temp-senior-design.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Python backend is running!"}

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup scheduler on shutdown"""
    scheduler.shutdown()
    logger.info("Scheduler shut down")
