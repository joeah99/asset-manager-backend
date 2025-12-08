import asyncio
import logging
from datetime import datetime
from db.asset_db import AssetDbContext
from db.valuation_db import ValuationDbContext
from services.asset_valuation_service import AssetValuationService
from models.asset_models import AssetDTO

logger = logging.getLogger(__name__)


class MonthlyAssetValuationJob:
    """
    Scheduled job that runs monthly to update asset valuations
    (equivalent to C# MonthlyAssetValuationJob using Quartz.NET)

    Runs at 1 AM on the first day of every month
    """

    def __init__(
        self,
        asset_db_context: AssetDbContext = None,
        valuation_db_context: ValuationDbContext = None,
        asset_valuation_service: AssetValuationService = None
    ):
        self.asset_db_context = asset_db_context or AssetDbContext()
        self.valuation_db_context = valuation_db_context or ValuationDbContext()
        self.asset_valuation_service = asset_valuation_service or AssetValuationService()

    async def get_all_assets_async(self):
        """Get all assets from database"""
        return await self.asset_db_context.get_all_assets_async()

    async def create_asset_valuation_async(self, asset: AssetDTO):
        """
        Create valuation for an asset based on its type

        Args:
            asset: Asset to value

        Raises:
            Exception: If valuation API call fails
        """
        try:
            if asset.type == "Equipment":
                equipment_valuation = await self.asset_valuation_service.get_equipment_valuation_async(
                    asset.manufacturer,
                    asset.model,
                    asset.model_year,
                    str(asset.usage),
                    asset.condition,
                    asset.country,
                    asset.state
                )

                await self.valuation_db_context.insert_equipment_valuation_async(
                    equipment_valuation,
                    asset.asset_id
                )

                logger.info(f"Created equipment valuation for asset {asset.asset_id}")

            elif asset.type == "Vehicle":
                vehicle_valuation = await self.asset_valuation_service.get_vehicle_valuation_async(
                    asset.manufacturer,
                    asset.model,
                    asset.model_year,
                    str(asset.usage),
                    asset.condition,
                    asset.country,
                    asset.state
                )

                await self.valuation_db_context.insert_vehicle_valuation_async(
                    vehicle_valuation,
                    asset.asset_id
                )

                logger.info(f"Created vehicle valuation for asset {asset.asset_id}")

        except Exception as e:
            logger.error(f"Failed to create valuation for asset {asset.asset_id}: {e}")
            raise

    async def execute(self):
        """
        Main job execution method
        Called by scheduler on the first day of every month at 1 AM
        """
        logger.info(f"Starting monthly asset valuation job at {datetime.now()}")

        try:
            assets = await self.get_all_assets_async()
            logger.info(f"Found {len(assets)} assets to value")

            success_count = 0
            failure_count = 0

            for asset in assets:
                try:
                    await self.create_asset_valuation_async(asset)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to value asset {asset.asset_id}: {e}")
                    failure_count += 1

            logger.info(
                f"Monthly asset valuation job completed. "
                f"Success: {success_count}, Failures: {failure_count}"
            )

        except Exception as e:
            logger.error(f"Monthly asset valuation job failed: {e}")
            raise


# Wrapper function for APScheduler (needs to be synchronous)
def run_monthly_valuation_job():
    """
    Synchronous wrapper for the async job execution
    This is called by APScheduler
    """
    job = MonthlyAssetValuationJob()
    asyncio.run(job.execute())
