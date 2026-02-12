from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import loan_routes, assets, scenarios, auth
from dotenv import load_dotenv
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    filename='backend_debug.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load .env values
load_dotenv()

app = FastAPI(title="Python Backend (Asset Manager Stage 2)")

db_url = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
DOTNET_API_BASE = os.getenv("DOTNET_API_BASE")

# Register routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(assets.router, prefix="", tags=["Assets"])
app.include_router(loan_routes.router, prefix="", tags=["LoanInformation"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])

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






