#!/usr/bin/env python
"""
Deployment configuration for NYC Taxi Duration Prediction Pipeline.
Runs every 2 minutes for learning purposes.
"""

from pipeline import duration_prediction_flow
from src.config import DEFAULT_YEAR, DEFAULT_MONTH


if __name__ == "__main__":
    print("\n🚀 Starting learning deployment (every 2 minutes)...")
    print("   Name: learning-training")
    print("   Schedule: */2 * * * *")
    print("   Timezone: America/Bogota")
    print(f"   Default year: {DEFAULT_YEAR}")
    print(f"   Default month: {DEFAULT_MONTH}")
    
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
    
    print("\n✅ Deployment is now running!")
    print("\n📋 The server is running and will execute the flow:")
    print("   - Every 2 minutes automatically")
    print("   - Press Ctrl+C to stop")
    print("\n� View executions at:")
    print("   - Prefect Cloud: https://app.prefect.cloud")
    print("   - Or local UI: http://localhost:4200")
    print("\n⏰ Next executions will be at:")
    print("   - In 2 minutes")
    print("   - In 4 minutes")
    print("   - In 6 minutes")
    print("   - And so on...")
