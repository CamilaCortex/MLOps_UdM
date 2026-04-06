"""
MLflow configuration and setup.
"""

import os
import logging
import mlflow
from prefect.blocks.system import Secret

from .constants import MLFLOW_EXPERIMENT_NAME, MLFLOW_DEFAULT_URI

logger = logging.getLogger(__name__)


def setup_mlflow():
    """Setup MLflow using Prefect Secret Block for secure configuration."""
    try:
        # Try to load MLflow URI from Prefect Secret
        mlflow_uri = Secret.load("mlflow-tracking-uri").get()
        logger.info("Loaded MLflow URI from Prefect Secret")
    except Exception:
        # Fallback to environment variable or local SQLite (expected behavior)
        mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", MLFLOW_DEFAULT_URI)
    
    try:
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.search_experiments()
        logger.info(f"Connected to MLflow at: {mlflow_uri}")
    except Exception as e:
        logger.warning(f"Failed to connect to {mlflow_uri}: {e}")
        logger.info("Falling back to local SQLite database")
        mlflow.set_tracking_uri(MLFLOW_DEFAULT_URI)
    
    try:
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        logger.info(f"Using MLflow experiment: {MLFLOW_EXPERIMENT_NAME}")
    except Exception as e:
        logger.error(f"Failed to set MLflow experiment: {e}")
        raise
