"""
Tax Policy Database Context

CRUD operations for the TaxPolicyYear table.
Follows the same asyncpg pattern as asset_db.py and loan_db.py.
"""

import asyncpg
import json
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class TaxPolicyRow:
    """Database row representation of a tax policy year"""
    tax_year: int
    section_179_limit: int
    section_179_phaseout_threshold: int
    bonus_depreciation_percent: int
    macrs_5yr_schedule: List[float]
    macrs_7yr_schedule: List[float]
    federal_brackets: List[dict]
    policy_source: str = "IRS Publication 946"
    last_updated: Optional[datetime] = None


class TaxPolicyDbContext:
    """Database operations for TaxPolicyYear table"""

    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv("POSTGRE_SQL_CONNECTIONSTRING")

    async def get_all_policies_async(self) -> List[TaxPolicyRow]:
        """Fetch all tax policy years from the database"""
        policies = []
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT "tax_year", "section_179_limit", "section_179_phaseout_threshold",
                       "bonus_depreciation_percent", "macrs_5yr_schedule", "macrs_7yr_schedule",
                       "federal_brackets", "policy_source", "last_updated"
                FROM "TaxPolicyYear"
                ORDER BY "tax_year"
            '''
            rows = await conn.fetch(query)
            for row in rows:
                policies.append(self._row_to_policy(row))
        finally:
            await conn.close()
        return policies

    async def get_policy_by_year_async(self, year: int) -> Optional[TaxPolicyRow]:
        """Fetch a single tax policy year"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                SELECT "tax_year", "section_179_limit", "section_179_phaseout_threshold",
                       "bonus_depreciation_percent", "macrs_5yr_schedule", "macrs_7yr_schedule",
                       "federal_brackets", "policy_source", "last_updated"
                FROM "TaxPolicyYear"
                WHERE "tax_year" = $1
            '''
            row = await conn.fetchrow(query, year)
            if not row:
                return None
            return self._row_to_policy(row)
        finally:
            await conn.close()

    async def upsert_policy_async(self, policy: TaxPolicyRow) -> TaxPolicyRow:
        """Insert or update a tax policy year (INSERT ... ON CONFLICT UPDATE)"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            query = '''
                INSERT INTO "TaxPolicyYear" (
                    "tax_year", "section_179_limit", "section_179_phaseout_threshold",
                    "bonus_depreciation_percent", "macrs_5yr_schedule", "macrs_7yr_schedule",
                    "federal_brackets", "policy_source", "last_updated"
                ) VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, $7::jsonb, $8, $9)
                ON CONFLICT ("tax_year") DO UPDATE SET
                    "section_179_limit" = EXCLUDED."section_179_limit",
                    "section_179_phaseout_threshold" = EXCLUDED."section_179_phaseout_threshold",
                    "bonus_depreciation_percent" = EXCLUDED."bonus_depreciation_percent",
                    "macrs_5yr_schedule" = EXCLUDED."macrs_5yr_schedule",
                    "macrs_7yr_schedule" = EXCLUDED."macrs_7yr_schedule",
                    "federal_brackets" = EXCLUDED."federal_brackets",
                    "policy_source" = EXCLUDED."policy_source",
                    "last_updated" = EXCLUDED."last_updated"
            '''
            await conn.execute(
                query,
                policy.tax_year,
                policy.section_179_limit,
                policy.section_179_phaseout_threshold,
                policy.bonus_depreciation_percent,
                json.dumps(policy.macrs_5yr_schedule),
                json.dumps(policy.macrs_7yr_schedule),
                json.dumps(policy.federal_brackets),
                policy.policy_source,
                policy.last_updated or datetime.now()
            )
            return policy
        finally:
            await conn.close()

    async def delete_policy_async(self, year: int) -> bool:
        """Delete a tax policy year. Returns True if a row was deleted."""
        conn = await asyncpg.connect(self.connection_string)
        try:
            result = await conn.execute(
                'DELETE FROM "TaxPolicyYear" WHERE "tax_year" = $1',
                year
            )
            return result.split()[-1] != '0'
        finally:
            await conn.close()

    def _row_to_policy(self, row) -> TaxPolicyRow:
        """Convert a database row to a TaxPolicyRow dataclass"""
        # asyncpg returns JSONB as Python dicts/lists automatically
        macrs_5 = row['macrs_5yr_schedule']
        macrs_7 = row['macrs_7yr_schedule']
        brackets = row['federal_brackets']

        # Handle case where JSONB came back as a string (shouldn't happen with asyncpg, but just in case)
        if isinstance(macrs_5, str):
            macrs_5 = json.loads(macrs_5)
        if isinstance(macrs_7, str):
            macrs_7 = json.loads(macrs_7)
        if isinstance(brackets, str):
            brackets = json.loads(brackets)

        return TaxPolicyRow(
            tax_year=row['tax_year'],
            section_179_limit=row['section_179_limit'],
            section_179_phaseout_threshold=row['section_179_phaseout_threshold'],
            bonus_depreciation_percent=row['bonus_depreciation_percent'],
            macrs_5yr_schedule=macrs_5,
            macrs_7yr_schedule=macrs_7,
            federal_brackets=brackets,
            policy_source=row['policy_source'],
            last_updated=row['last_updated']
        )
