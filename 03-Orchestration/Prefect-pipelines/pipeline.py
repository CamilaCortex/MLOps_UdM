#!/usr/bin/env python
"""
NYC Taxi Duration Prediction Pipeline - Modular Architecture
Main orchestration flow using Prefect with domain-driven design.
"""

import logging
import mlflow
from prefect import flow, get_run_logger
from prefect.artifacts import create_markdown_artifact

from src.config import setup_mlflow, TARGET_COLUMN, MLFLOW_EXPERIMENT_NAME, MLFLOW_UI_URL
from src.data import read_dataframe, validate_data, calculate_next_period, find_latest_available_period
from src.features import create_features
from src.models import optimize_hyperparameters, train_model, register_best_model

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
def duration_prediction_flow(year: int | None = None, month: int | None = None) -> str:
    """
    Main pipeline flow for NYC taxi duration prediction.

    Args:
        year: Year of training data (uses default if None)
        month: Month of training data (uses default if None)

    Returns:
        MLflow run ID
    """
    logger = get_run_logger()

    # Si no se especifica year/month, se detecta automáticamente el periodo
    # más reciente que la TLC ya tenga publicado (en vez de usar siempre
    # DEFAULT_YEAR/DEFAULT_MONTH, que quedarían fijos en el tiempo). Esto es
    # lo que permite que un deployment programado (ver deploy.py) reentrene
    # cada mes con datos realmente nuevos, sin tener que re-desplegar el
    # flow cada vez que cambia el mes.
    if year is None or month is None:
        logger.info("year/month no especificados: detectando el periodo más reciente disponible en TLC...")
        year, month = find_latest_available_period()
        logger.info(f"Periodo detectado: entrenamiento {year}-{month:02d}")

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
    model_run_id, rmse = train_model(X_train, y_train, X_val, y_val, dv, best_params)

    # Register best model in MLflow Model Registry
    logger.info("Registering best model in MLflow Model Registry...")
    model_version = register_best_model(
        run_id=model_run_id,
        rmse=rmse,
        model_name="nyc-taxi-duration-predictor"
    )
    logger.info(f"Model registered as version {model_version}")

    # Create final pipeline artifact with enhanced information
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
    - **MLflow Run ID**: [{model_run_id}]({MLFLOW_UI_URL})
    - **MLflow Experiment**: {MLFLOW_EXPERIMENT_NAME}
    - **Registered Model**: nyc-taxi-duration-predictor v{model_version}

    ## Next Steps
    1. [Review model in MLflow Model Registry]({MLFLOW_UI_URL}/#/models/nyc-taxi-duration-predictor)
    2. La version se registra con el alias "candidate"; solo se promueve a "champion"
       si mejora el RMSE del champion actual (ver register_best_model)
    3. Use deployment module to serve the registered model
    4. Compare with previous model versions

    ## Quick Links
    - [Prefect Cloud Dashboard](https://app.prefect.cloud)
    - [MLflow Tracking UI]({MLFLOW_UI_URL})
    """

    create_markdown_artifact(
        key="pipeline-summary",
        markdown=pipeline_summary,
        description="Complete pipeline execution summary"
    )

    return model_run_id


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train a model to predict taxi trip duration using Prefect.')
    parser.add_argument('--year', type=int, default=None, help='Year of the data to train on (default: se detecta automáticamente el periodo más reciente disponible)')
    parser.add_argument('--month', type=int, default=None, help='Month of the data to train on (default: se detecta automáticamente el periodo más reciente disponible)')
    args = parser.parse_args()

    try:
        # Run the flow
        model_run_id = duration_prediction_flow(year=args.year, month=args.month)
        print("\nPipeline completed successfully!")
        print(f"MLflow run_id: {model_run_id}")
        print(f"View results at: {mlflow.get_tracking_uri()}")
        print(f"Model registered in MLflow Model Registry: nyc-taxi-duration-predictor")

        # Save run ID for reference
        with open("prefect_run_id.txt", "w") as f:
            f.write(model_run_id)
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


 # uv run mlflow ui --backend-store-uri sqlite:///mlflow.db      
#  uv run mlflow server \
#   --host 127.0.0.1 \
#   --port 5000 \
#   --backend-store-uri sqlite:///mlflow.db \
#   --default-artifact-root ./mlruns \
#   --allowed-hosts "localhost,127.0.0.1,127.0.0.1:5000"                                        