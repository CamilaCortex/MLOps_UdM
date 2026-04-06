#!/usr/bin/env python
"""
NYC Taxi Duration Prediction Pipeline - Modular Architecture
Main orchestration flow using Prefect with domain-driven design.
"""

import logging
import mlflow
from prefect import flow, get_run_logger
from prefect.artifacts import create_markdown_artifact

from src.config import setup_mlflow, DEFAULT_YEAR, DEFAULT_MONTH, TARGET_COLUMN, MLFLOW_EXPERIMENT_NAME
from src.data import read_dataframe, validate_data, calculate_next_period
from src.features import create_features
from src.models import optimize_hyperparameters, train_model

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MLflow
setup_mlflow()


@flow(
    name="NYC Taxi Duration Prediction Pipeline",
    description="End-to-end ML pipeline for taxi duration prediction with Optuna optimization",
    log_prints=True
)
def duration_prediction_flow(year: int = None, month: int = None) -> str:
    """
    Main pipeline flow for NYC taxi duration prediction.

    Args:
        year: Year of training data (uses default if None)
        month: Month of training data (uses default if None)

    Returns:
        MLflow run ID
    """
    logger = get_run_logger()
    
    # Use defaults if not provided
    if year is None:
        year = DEFAULT_YEAR
    
    if month is None:
        month = DEFAULT_MONTH
    
    # Load training data
    df_train = read_dataframe(year=year, month=month)
    
    # Validate training data
    df_train = validate_data(df_train)

    # Calculate validation data period
    next_year, next_month = calculate_next_period(year, month)
    
    # Load validation data
    df_val = read_dataframe(year=next_year, month=next_month)
    
    # Validate validation data
    df_val = validate_data(df_val)

    # Create features
    X_train, dv = create_features(df_train)
    X_val, _ = create_features(df_val, dv)

    # Prepare targets
    y_train = df_train[TARGET_COLUMN].values
    y_val = df_val[TARGET_COLUMN].values

    # Optimize hyperparameters with Optuna
    logger.info("Starting hyperparameter optimization...")
    best_params = optimize_hyperparameters(X_train, y_train, X_val, y_val)
    
    # Train model with optimized parameters
    logger.info("Training final model with optimized parameters...")
    run_id, rmse = train_model(X_train, y_train, X_val, y_val, dv, best_params)

    # Create final pipeline artifact with enhanced information
    mlflow_ui_url = mlflow.get_tracking_uri().replace('sqlite:///', 'http://localhost:5000/')
    
    pipeline_summary = f"""
    # Pipeline Execution Summary

    ## Data
    - **Training Period**: {year}-{month:02d}
    - **Validation Period**: {next_year}-{next_month:02d}
    - **Training Samples**: {len(y_train):,}
    - **Validation Samples**: {len(y_val):,}
    - **Features**: {X_train.shape[1]:,}

    ## Results
    - **RMSE**: {rmse:.4f}
    - **MLflow Run ID**: [{run_id}]({mlflow_ui_url})
    - **MLflow Experiment**: {MLFLOW_EXPERIMENT_NAME}

    ## Next Steps
    1. [Review model performance in MLflow UI]({mlflow_ui_url})
    2. Compare with previous runs in Prefect Cloud
    3. Check artifacts for detailed metrics
    4. Consider model deployment if RMSE < threshold
    
    ## Quick Links
    - [Prefect Cloud Dashboard](https://app.prefect.cloud)
    - [MLflow Tracking UI]({mlflow_ui_url})
    """

    create_markdown_artifact(
        key="pipeline-summary",
        markdown=pipeline_summary,
        description="Complete pipeline execution summary"
    )

    return run_id


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train a model to predict taxi trip duration using Prefect.')
    parser.add_argument('--year', type=int, default=DEFAULT_YEAR, help=f'Year of the data to train on (default: {DEFAULT_YEAR})')
    parser.add_argument('--month', type=int, default=DEFAULT_MONTH, help=f'Month of the data to train on (default: {DEFAULT_MONTH})')
    args = parser.parse_args()

    try:
        # Run the flow
        run_id = duration_prediction_flow(year=args.year, month=args.month)
        print("\nPipeline completed successfully!")
        print(f"MLflow run_id: {run_id}")
        print(f"View results at: {mlflow.get_tracking_uri()}")

        # Save run ID for reference
        with open("prefect_run_id.txt", "w") as f:
            f.write(run_id)
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
