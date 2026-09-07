"""
Model Registry task for MLflow Model Registry.
Handles registration of the best model obtained from training.

Usa aliases del Model Registry ("champion" / "candidate") en lugar del
sistema de stages (None -> Staging -> Production -> Archived), que MLflow
tiene deprecado. Cada modelo nuevo se registra siempre como "candidate";
solo se promueve a "champion" si su RMSE mejora al del champion actual.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import mlflow
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from prefect import task, get_run_logger
from prefect.artifacts import create_markdown_artifact

from ..config import MLFLOW_UI_URL, CHAMPION_ALIAS, CANDIDATE_ALIAS


@task(name="register_best_model", description="Register best model in MLflow Model Registry")
def register_best_model(
    run_id: str,
    rmse: float,
    model_name: str = "nyc-taxi-duration-predictor"
) -> str:
    """
    Register the best trained model in MLflow Model Registry.

    The new version is always tagged with the "candidate" alias. It is
    additionally promoted to "champion" only if its RMSE is better than
    (lower than) the RMSE of the current champion, or if there is no
    champion yet.

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
        model_uri = f"runs:/{run_id}/models_mlflow"

        logger.info(f"Registering model from run: {run_id}")
        logger.info(f"Model URI: {model_uri}")

        model_details = mlflow.register_model(model_uri=model_uri, name=model_name)
        version = model_details.version
        logger.info(f"Model registered successfully as '{model_name}' version {version}")

        # Metadata and tags for the new version
        client.update_model_version(
            name=model_name,
            version=version,
            description=(
                f"XGBoost model for NYC taxi duration prediction. "
                f"RMSE: {rmse:.4f} minutes. Trained with Optuna optimization."
            )
        )
        client.set_model_version_tag(name=model_name, version=version, key="rmse", value=f"{rmse:.4f}")
        client.set_model_version_tag(name=model_name, version=version, key="model_type", value="xgboost")
        client.set_model_version_tag(name=model_name, version=version, key="framework", value="prefect+mlflow")
        client.set_model_version_tag(name=model_name, version=version, key="optimization", value="optuna")
        logger.info(f"Model version {version} tagged with metadata")

        # Every new version is a candidate for promotion
        client.set_registered_model_alias(name=model_name, alias=CANDIDATE_ALIAS, version=version)
        logger.info(f"Model version {version} tagged as '{CANDIDATE_ALIAS}'")

        # Compare against the current champion (if any) before promoting
        champion_rmse = _get_champion_rmse(client, model_name)
        promoted_to_champion = champion_rmse is None or rmse < champion_rmse

        if promoted_to_champion:
            client.set_registered_model_alias(name=model_name, alias=CHAMPION_ALIAS, version=version)
            if champion_rmse is None:
                logger.info(f"No previous champion found. Version {version} promoted to '{CHAMPION_ALIAS}'.")
            else:
                logger.info(
                    f"Version {version} (RMSE {rmse:.4f}) improves on the current "
                    f"champion (RMSE {champion_rmse:.4f}). Promoted to '{CHAMPION_ALIAS}'."
                )
        else:
            logger.info(
                f"Version {version} (RMSE {rmse:.4f}) does not improve on the current "
                f"champion (RMSE {champion_rmse:.4f}). Stays as '{CANDIDATE_ALIAS}'."
            )

        # Save model locally
        local_model_path = _save_model_locally(run_id, model_name, version, rmse, logger)

        # Create Prefect artifact with registration details
        registration_summary = _build_registration_summary(
            model_name=model_name,
            version=version,
            rmse=rmse,
            run_id=run_id,
            champion_rmse=champion_rmse,
            promoted_to_champion=promoted_to_champion,
            local_model_path=local_model_path,
        )

        create_markdown_artifact(
            key="model-registration",
            markdown=registration_summary,
            description=f"Model {model_name} v{version} registration details"
        )

        logger.info("Registration artifact created successfully")

        return str(version)

    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        logger.error(f"Run ID: {run_id}")
        logger.error(f"Model Name: {model_name}")
        raise


def _get_champion_rmse(client: MlflowClient, model_name: str) -> Optional[float]:
    """
    Return the RMSE of the current "champion" model version, or None if no
    champion alias has been set yet (e.g. first run of the pipeline).

    Args:
        client: MLflow tracking client
        model_name: Name of the registered model

    Returns:
        RMSE of the current champion as float, or None
    """
    try:
        champion_version = client.get_model_version_by_alias(model_name, CHAMPION_ALIAS)
    except MlflowException:
        return None

    rmse_tag = champion_version.tags.get("rmse")
    if rmse_tag is None:
        return None

    try:
        return float(rmse_tag)
    except ValueError:
        return None


def _build_registration_summary(
    model_name: str,
    version: str,
    rmse: float,
    run_id: str,
    champion_rmse: Optional[float],
    promoted_to_champion: bool,
    local_model_path: str,
) -> str:
    """Build the markdown content for the registration Prefect artifact."""

    if promoted_to_champion:
        status_line = f"Promoted to **{CHAMPION_ALIAS}**"
    else:
        status_line = f"Kept as **{CANDIDATE_ALIAS}** (did not beat the current champion)"

    if champion_rmse is None:
        comparison_line = "No previous champion existed, so this version became the champion."
    else:
        diff_pct = (champion_rmse - rmse) / champion_rmse * 100
        comparison_line = (
            f"Current champion RMSE was {champion_rmse:.4f} minutes "
            f"({diff_pct:+.2f}% change with this version)."
        )

    return f"""
    # Model Registration Summary

    ## Registered Model
    - **Model Name**: {model_name}
    - **Version**: {version}
    - **RMSE**: {rmse:.4f} minutes
    - **MLflow Run ID**: [{run_id}]({MLFLOW_UI_URL})
    - **Status**: {status_line}

    ## Comparison Against Current Champion
    {comparison_line}

    ## Model URIs
    ```
    models:/{model_name}@{CANDIDATE_ALIAS}
    models:/{model_name}@{CHAMPION_ALIAS}
    ```

    ## Local Model Path
    ```
    {local_model_path}
    ```

    ## Next Steps
    1. Review model in [MLflow Model Registry]({MLFLOW_UI_URL}/#/models/{model_name})
    2. Deploy model using batch deployment module
    3. Monitor predictions and performance

    ## Deployment Command
    ```python
    # Always loads whichever version currently holds the "champion" alias
    model_uri = "models:/{model_name}@{CHAMPION_ALIAS}"
    model = mlflow.xgboost.load_model(model_uri)
    ```
    """


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
        models_dir = Path("models") / "registered"
        models_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = models_dir / f"v{version}_{timestamp}"
        model_dir.mkdir(exist_ok=True)

        logger.info(f"Saving model locally to: {model_dir}")

        model_uri = f"runs:/{run_id}/models_mlflow"
        local_model_path = mlflow.artifacts.download_artifacts(
            artifact_uri=model_uri,
            dst_path=str(model_dir)
        )

        preprocessor_uri = f"runs:/{run_id}/preprocessor"
        preprocessor_path = mlflow.artifacts.download_artifacts(
            artifact_uri=preprocessor_uri,
            dst_path=str(model_dir)
        )

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

        logger.info(f"Model saved locally at: {model_dir}")
        logger.info(f"  - Model artifacts: {local_model_path}")
        logger.info(f"  - Preprocessor: {preprocessor_path}")
        logger.info(f"  - Metadata: {metadata_file}")

        return str(model_dir)

    except Exception as e:
        logger.warning(f"Failed to save model locally: {e}")
        logger.warning("Model is still registered in MLflow Registry")
        return "Local save failed - check logs"
