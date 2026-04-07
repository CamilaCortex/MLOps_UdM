"""
Model Registry task for MLflow Model Registry.
Handles registration of the best model obtained from training.
"""

import mlflow
from mlflow.tracking import MlflowClient
from prefect import task, get_run_logger
from prefect.artifacts import create_markdown_artifact
from pathlib import Path
import json
from datetime import datetime


@task(name="register_best_model", description="Register best model in MLflow Model Registry")
def register_best_model(
    run_id: str,
    rmse: float,
    model_name: str = "nyc-taxi-duration-predictor"
) -> str:
    """
    Register the best trained model in MLflow Model Registry.
    
    This task takes the model from a successful training run and registers it
    in the MLflow Model Registry for version control and deployment.
    
    Args:
        run_id: MLflow run ID containing the trained model
        rmse: RMSE metric of the model
        model_name: Name for the registered model in the registry
    
    Returns:
        Model version number as string
    """
    logger = get_run_logger()
    client = MlflowClient()
    
    try:
        # Construct model URI from run_id
        model_uri = f"runs:/{run_id}/models_mlflow"
        
        logger.info(f"Registering model from run: {run_id}")
        logger.info(f"Model URI: {model_uri}")
        
        # Register the model in MLflow Model Registry
        model_details = mlflow.register_model(
            model_uri=model_uri,
            name=model_name
        )
        
        version = model_details.version
        logger.info(f"✅ Model registered successfully as '{model_name}' version {version}")
        
        # Add metadata to the model version
        client.update_model_version(
            name=model_name,
            version=version,
            description=f"XGBoost model for NYC taxi duration prediction. RMSE: {rmse:.4f} minutes. Trained with Optuna optimization."
        )
        
        # Set tags for tracking and filtering
        client.set_model_version_tag(
            name=model_name,
            version=version,
            key="rmse",
            value=f"{rmse:.4f}"
        )
        
        client.set_model_version_tag(
            name=model_name,
            version=version,
            key="model_type",
            value="xgboost"
        )
        
        client.set_model_version_tag(
            name=model_name,
            version=version,
            key="framework",
            value="prefect+mlflow"
        )
        
        client.set_model_version_tag(
            name=model_name,
            version=version,
            key="optimization",
            value="optuna"
        )
        
        logger.info(f"Model version {version} tagged with metadata")
        
        # Promote model to Production automatically
        logger.info(f"Promoting model version {version} to Production...")
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production",
            archive_existing_versions=True
        )
        logger.info(f"✅ Model version {version} promoted to Production")
        
        # Save model locally
        local_model_path = _save_model_locally(run_id, model_name, version, rmse, logger)
        
        # Create Prefect artifact with registration details
        mlflow_ui_url = mlflow.get_tracking_uri().replace('sqlite:///', 'http://localhost:5000/')
        
        registration_summary = f"""
        # Model Registration Summary
        
        ## Registered Model
        - **Model Name**: {model_name}
        - **Version**: {version}
        - **Stage**: Production ✅
        - **RMSE**: {rmse:.4f} minutes
        - **MLflow Run ID**: [{run_id}]({mlflow_ui_url})
        
        ## Model URI (Production)
        ```
        models:/{model_name}/Production
        ```
        
        ## Local Model Path
        ```
        {local_model_path}
        ```
        
        ## Model Ready for Deployment
        ✅ Model trained with Optuna optimization
        ✅ Registered in MLflow Model Registry
        ✅ Promoted to Production stage
        ✅ Saved locally for backup
        
        ## Next Steps
        1. Review model in [MLflow Model Registry]({mlflow_ui_url}/#/models/{model_name})
        2. Deploy model using batch deployment module
        3. Monitor predictions and performance
        
        ## Deployment Command
        ```bash
        # Load model for deployment
        model_uri = "models:/{model_name}/Production"
        model = mlflow.xgboost.load_model(model_uri)
        ```
        """
        
        create_markdown_artifact(
            key="model-registration",
            markdown=registration_summary,
            description=f"Model {model_name} v{version} registration details"
        )
        
        logger.info(f"Registration artifact created successfully")
        
        return str(version)
        
    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        logger.error(f"Run ID: {run_id}")
        logger.error(f"Model Name: {model_name}")
        raise


def _save_model_locally(run_id: str, model_name: str, version: str, rmse: float, logger) -> str:
    """
    Save model locally for backup and offline use.
    
    Args:
        run_id: MLflow run ID
        model_name: Name of the model
        version: Model version
        rmse: RMSE metric
        logger: Prefect logger
    
    Returns:
        Path to saved model directory
    """
    try:
        # Create models directory structure
        models_dir = Path("models") / "registered"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Create version-specific directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = models_dir / f"v{version}_{timestamp}"
        model_dir.mkdir(exist_ok=True)
        
        logger.info(f"Saving model locally to: {model_dir}")
        
        # Download model from MLflow
        model_uri = f"runs:/{run_id}/models_mlflow"
        local_model_path = mlflow.artifacts.download_artifacts(
            artifact_uri=model_uri,
            dst_path=str(model_dir)
        )
        
        # Download preprocessor
        preprocessor_uri = f"runs:/{run_id}/preprocessor"
        preprocessor_path = mlflow.artifacts.download_artifacts(
            artifact_uri=preprocessor_uri,
            dst_path=str(model_dir)
        )
        
        # Save metadata
        metadata = {
            "model_name": model_name,
            "version": version,
            "run_id": run_id,
            "rmse": rmse,
            "timestamp": timestamp,
            "model_path": str(local_model_path),
            "preprocessor_path": str(preprocessor_path),
            "mlflow_uri": f"models:/{model_name}/{version}"
        }
        
        metadata_file = model_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Model saved locally at: {model_dir}")
        logger.info(f"   - Model artifacts: {local_model_path}")
        logger.info(f"   - Preprocessor: {preprocessor_path}")
        logger.info(f"   - Metadata: {metadata_file}")
        
        return str(model_dir)
        
    except Exception as e:
        logger.warning(f"Failed to save model locally: {e}")
        logger.warning("Model is still registered in MLflow Registry")
        return "Local save failed - check logs"
