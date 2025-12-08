# Python Backend - Asset Manager

This is the Python FastAPI backend for the Asset Manager application, converted from the original C# .NET backend.

## Features

- **Authentication** - User registration, login, password reset (SendGrid email integration)
- **Asset Management** - CRUD operations for equipment and vehicles
- **Valuations** - Integration with EquipmentWatch and PriceDigest APIs for real-time asset valuations
- **Depreciation** - Support for 5 depreciation methods (Straight-line, Declining Balance, Double Declining, Units of Production, MACRS)
- **Loan Management** - Loan tracking with amortization schedules and impact analysis
- **Scheduled Jobs** - Monthly automatic asset valuation updates (APScheduler)

## Requirements

- Python 3.8+
- PostgreSQL database
- API keys for EquipmentWatch and PriceDigest (for asset valuations)
- SendGrid API key (for email functionality)

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**

   Create a `.env` file in the `Backend/python-backend` directory:
   ```env
   POSTGRE_SQL_CONNECTIONSTRING=postgresql://user:password@localhost:5432/database
   EQUIPMENT_WATCH_API_KEY=your_equipment_watch_api_key
   PRICE_DIGEST_API_KEY=your_price_digest_api_key
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```

3. **Ensure PostgreSQL database is running** with the required schema

## Running the Server

### Development Mode

```bash
# From the python-backend directory
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication (`/api`)
- `POST /api/Register` - Register new user
- `POST /api/Login` - User login
- `POST /api/ForgotPassword` - Request password reset
- `POST /api/ChangePassword` - Change password
- `DELETE /api/DeleteUser` - Delete user account
- `PUT /api/UpdateUser` - Update user information

### Assets (`/api`)
- `GET /api/GetAssets?user_id={id}` - Get all assets for a user
- `POST /api/CreateAsset` - Create new asset
- `PUT /api/UpdateAsset` - Update existing asset
- `DELETE /api/DeleteAsset` - Delete asset (soft delete)

### Valuations (`/Valuation`)
- `GET /Valuation/?user_id={id}` - Get all equipment valuations
- `GET /Valuation/total-fmv?user_id={id}` - Get monthly total fair market values (last 12 months)
- `GET /Valuation/total-Asset-Value?user_id={id}` - Get total asset value with year-over-year change
- `GET /Valuation/adjusted-forced-liquidation?user_id={id}` - Get adjusted forced liquidation values

### Loans (`/api/loans`)
- `GET /api/loans/get-loans?user_id={id}` - Get all loans for a user
- `POST /api/loans/create` - Create new loan
- `PUT /api/loans/update` - Update existing loan
- `DELETE /api/loans/delete` - Delete loan
- `POST /api/loans/impact/liquidation` - Calculate liquidation impact
- `POST /api/loans/impact/replacement` - Calculate replacement impact

### Commodities (`/api/commodities`)
- `GET /api/commodities/` - Get commodity data

## Scheduled Jobs

The backend includes an automated monthly job that runs at **1 AM on the 1st of every month** to update all asset valuations automatically.

## Architecture

```
python-backend/
├── main.py                 # FastAPI app initialization, routes, scheduler
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not in git)
│
├── routes/                # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── assets.py         # Asset endpoints
│   ├── valuations.py     # Valuation endpoints
│   ├── loans.py          # Loan endpoints
│   └── commodities.py    # Commodity endpoints
│
├── managers/             # Business logic orchestration
│   ├── account_manager.py
│   ├── asset_manager.py
│   ├── asset_depreciation_manager.py
│   ├── valuation_manager.py
│   └── loan_manager.py
│
├── services/             # Core business services
│   ├── asset_valuation_service.py      # External API integration
│   ├── asset_depreciation_service.py   # Depreciation calculations
│   ├── loan_service.py                 # Loan amortization
│   ├── loan_impact_service.py          # Loan impact analysis
│   ├── email_service.py                # SendGrid integration
│   ├── password_reset_service.py       # Password reset tokens
│   └── monthly_asset_valuation_job.py  # Scheduled job
│
├── db/                   # Database access layer
│   ├── auth_db.py
│   ├── asset_db.py
│   ├── asset_depreciation_db.py
│   ├── valuation_db.py
│   └── loan_db.py
│
└── models/               # Pydantic data models
    ├── auth_models.py
    ├── asset_models.py
    ├── valuation_models.py
    └── loan_models.py
```

## Differences from C# Backend

### Improvements
- **Better loan amortization**: Proper interest vs. principal split per payment
- **New feature**: Loan impact analysis (liquidation/replacement scenarios)
- **Simpler architecture**: Using FastAPI's dependency injection and Pydantic validation
- **Better async support**: Full async/await throughout the stack

### Compatibility
- All API endpoints match the C# backend for frontend compatibility
- Field naming conventions preserved using Pydantic field aliases
- Database schema unchanged

## Testing

Run tests with pytest:
```bash
pytest
```

## Frontend Configuration

The frontend should point to this backend by setting in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Switching Between Backends

To switch back to the C# backend, update the frontend `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://localhost:5001
```

Both backends can run simultaneously on different ports without conflicts.
