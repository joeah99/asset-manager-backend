"""
Seed Tax Policies Migration

Inserts the default 2024–2027 tax policy data into the TaxPolicyYear table.
Safe to run multiple times — uses INSERT ... ON CONFLICT DO NOTHING.

Usage:
    cd Backend
    python -m migrations.seed_tax_policies
"""

import asyncio
import json
import os
from dotenv import load_dotenv
import asyncpg
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# The same data that was previously hardcoded in tax_policy_service.py
SEED_POLICIES = [
    {
        "tax_year": 2024,
        "section_179_limit": 1_220_000,
        "section_179_phaseout_threshold": 3_050_000,
        "bonus_depreciation_percent": 60,
        "macrs_5yr_schedule": [20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
        "macrs_7yr_schedule": [14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
        "federal_brackets": [
            {"limit": 11600, "rate": 0.10},
            {"limit": 47150, "rate": 0.12},
            {"limit": 100525, "rate": 0.22},
            {"limit": 191950, "rate": 0.24},
            {"limit": 243725, "rate": 0.32},
            {"limit": 609350, "rate": 0.35},
            {"limit": 999999999, "rate": 0.37}
        ],
        "policy_source": "IRS Rev. Proc. 2023-34"
    },
    {
        "tax_year": 2025,
        "section_179_limit": 1_250_000,
        "section_179_phaseout_threshold": 3_130_000,
        "bonus_depreciation_percent": 40,
        "macrs_5yr_schedule": [20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
        "macrs_7yr_schedule": [14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
        "federal_brackets": [
            {"limit": 11925, "rate": 0.10},
            {"limit": 48475, "rate": 0.12},
            {"limit": 103350, "rate": 0.22},
            {"limit": 197300, "rate": 0.24},
            {"limit": 250525, "rate": 0.32},
            {"limit": 626350, "rate": 0.35},
            {"limit": 999999999, "rate": 0.37}
        ],
        "policy_source": "IRS Rev. Proc. 2024-40 (projected)"
    },
    {
        "tax_year": 2026,
        "section_179_limit": 2_560_000,
        "section_179_phaseout_threshold": 4_090_000,
        "bonus_depreciation_percent": 100,
        "macrs_5yr_schedule": [20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
        "macrs_7yr_schedule": [14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
        "federal_brackets": [
            {"limit": 12225, "rate": 0.10},
            {"limit": 49700, "rate": 0.12},
            {"limit": 105950, "rate": 0.22},
            {"limit": 202250, "rate": 0.24},
            {"limit": 256800, "rate": 0.32},
            {"limit": 642050, "rate": 0.35},
            {"limit": 999999999, "rate": 0.37}
        ],
        "policy_source": "Projected (TCJA Phaseout)"
    },
    {
        "tax_year": 2027,
        "section_179_limit": 1_310_000,
        "section_179_phaseout_threshold": 3_290_000,
        "bonus_depreciation_percent": 0,
        "macrs_5yr_schedule": [20.00, 32.00, 19.20, 11.52, 11.52, 5.76],
        "macrs_7yr_schedule": [14.29, 24.49, 17.49, 12.49, 8.93, 8.92, 8.93, 4.46],
        "federal_brackets": [
            {"limit": 12525, "rate": 0.10},
            {"limit": 50950, "rate": 0.12},
            {"limit": 108600, "rate": 0.22},
            {"limit": 207300, "rate": 0.24},
            {"limit": 263200, "rate": 0.32},
            {"limit": 658100, "rate": 0.35},
            {"limit": 999999999, "rate": 0.37}
        ],
        "policy_source": "Projected (TCJA Expiration)"
    }
]


async def seed_tax_policies():
    """Insert default tax policy data. Safe to run multiple times."""
    db_url = os.getenv("POSTGRE_SQL_CONNECTIONSTRING")
    if not db_url:
        logger.error("POSTGRE_SQL_CONNECTIONSTRING not set.")
        return

    conn = await asyncpg.connect(db_url)
    try:
        for policy in SEED_POLICIES:
            query = '''
                INSERT INTO "TaxPolicyYear" (
                    "tax_year", "section_179_limit", "section_179_phaseout_threshold",
                    "bonus_depreciation_percent", "macrs_5yr_schedule", "macrs_7yr_schedule",
                    "federal_brackets", "policy_source", "last_updated"
                ) VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7::jsonb, $8, CURRENT_TIMESTAMP)
                ON CONFLICT ("tax_year") DO NOTHING
            '''
            status = await conn.execute(
                query,
                policy["tax_year"],
                policy["section_179_limit"],
                policy["section_179_phaseout_threshold"],
                policy["bonus_depreciation_percent"],
                json.dumps(policy["macrs_5yr_schedule"]),
                json.dumps(policy["macrs_7yr_schedule"]),
                json.dumps(policy["federal_brackets"]),
                policy["policy_source"]
            )
            if status == "INSERT 0 1":
                logger.info(f"Seeded new tax policy for year {policy['tax_year']}")

        # logger.info("Tax policy seeding checked.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_tax_policies())
