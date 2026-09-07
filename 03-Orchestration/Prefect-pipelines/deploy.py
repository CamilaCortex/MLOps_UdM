#!/usr/bin/env python
"""
Deployment configuration for NYC Taxi Duration Prediction Pipeline.
Runs every 2 minutes for learning purposes.
"""

import logging

from pipeline import duration_prediction_flow
from src.config import DEFAULT_YEAR, DEFAULT_MONTH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting learning deployment (every 2 minutes)...")
    logger.info("Name: learning-training")
    logger.info("Schedule: */2 * * * *")
    logger.info("Timezone: America/Bogota")
    logger.info(f"Default year: {DEFAULT_YEAR}")
    logger.info(f"Default month: {DEFAULT_MONTH}")

    # Serve the flow with schedule
    duration_prediction_flow.serve(
        name="learning-training",
        cron="*/2 * * * *",
        tags=["learning", "testing", "ml"],
        description="Train model every 2 minutes for learning purposes",
        parameters={
            "year": DEFAULT_YEAR,  # Use default from config
            "month": DEFAULT_MONTH
        }
    )

    logger.info("Deployment is now running.")
    logger.info("The server is running and will execute the flow:")
    logger.info("  - Every 2 minutes automatically")
    logger.info("  - Press Ctrl+C to stop")
    logger.info("View executions at:")
    logger.info("  - Prefect Cloud: https://app.prefect.cloud")
    logger.info("  - Or local UI: http://localhost:4200")
    logger.info("Next executions will be at:")
    logger.info("  - In 2 minutes")
    logger.info("  - In 4 minutes")
    logger.info("  - In 6 minutes")
    logger.info("  - And so on...")
