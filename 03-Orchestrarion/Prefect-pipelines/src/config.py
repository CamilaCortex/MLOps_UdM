"""
Configuration and MLflow setup for the pipeline.
"""

import os
import logging
import mlflow
from prefect.blocks.system import Secret

logger = logging.getLogger(__name__)


def setup_mlflow():
    """Setup MLflow using Prefect Secret Block for secure configuration."""
    try:
        # Try to load MLflow URI from Prefect Secret
        mlflow_uri = Secret.load("mlflow-tracking-uri").get()
        logger.info("Loaded MLflow URI from Prefect Secret")
    except Exception:
        # Fallback to environment variable or local SQLite (expected behavior)
        mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    
    try:
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.search_experiments()
        logger.info(f"Connected to MLflow at: {mlflow_uri}")
    except Exception as e:
        logger.warning(f"Failed to connect to {mlflow_uri}: {e}")
        logger.info("Falling back to local SQLite database")
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
    
    try:
        experiment_name = "nyc-taxi-experiment-prefect"
        mlflow.set_experiment(experiment_name)
        logger.info(f"Using MLflow experiment: {experiment_name}")
    except Exception as e:
        logger.error(f"Failed to set MLflow experiment: {e}")
        raise


# Pipeline constants
DEFAULT_YEAR = 2025
DEFAULT_MONTH = 1
MIN_RECORDS = 1000
OPTUNA_TRIALS = 20
NULL_THRESHOLD = 10.0
