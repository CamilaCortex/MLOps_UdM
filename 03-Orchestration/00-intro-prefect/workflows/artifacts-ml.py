"""
Ejemplos de Artifacts de Prefect para Machine Learning.

Los artifacts permiten visualizar resultados, métricas y datos
directamente en Prefect Cloud sin necesidad de herramientas externas.
"""

from prefect import flow, task, get_run_logger
from prefect.artifacts import (
    create_markdown_artifact,
    create_table_artifact,
    create_link_artifact,
)
import pandas as pd
from datetime import datetime


@task
def train_model_simulation():
    """Simula entrenamiento de un modelo y retorna métricas."""
    logger = get_run_logger()
    logger.info("Training model...")
    
    # Simular métricas de entrenamiento
    metrics = {
        "rmse": 7.1547,
        "mae": 5.2341,
        "r2": 0.8234,
        "training_time": 45.2,
        "n_samples": 46307,
        "n_features": 448
    }
    
    return metrics


@task
def create_metrics_summary(metrics: dict):
    """Crea un artifact de markdown con resumen de métricas."""
    
    markdown_content = f"""
# 📊 Model Training Summary

## Performance Metrics

| Metric | Value |
|--------|-------|
| RMSE | {metrics['rmse']:.4f} |
| MAE | {metrics['mae']:.4f} |
| R² Score | {metrics['r2']:.4f} |

## Training Details

- **Training Time**: {metrics['training_time']:.1f} seconds
- **Samples**: {metrics['n_samples']:,}
- **Features**: {metrics['n_features']}
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status

✅ Model trained successfully!

### Next Steps
1. Validate on test set
2. Compare with baseline
3. Deploy if performance improves
"""
    
    create_markdown_artifact(
        key="model-training-summary",
        markdown=markdown_content,
        description="Summary of model training metrics and details"
    )


@task
def create_metrics_table(metrics: dict):
    """Crea un artifact de tabla con métricas detalladas."""
    
    # Simular comparación con runs anteriores
    comparison_data = [
        {
            "run_id": "current",
            "rmse": metrics['rmse'],
            "mae": metrics['mae'],
            "r2": metrics['r2'],
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M')
        },
        {
            "run_id": "baseline",
            "rmse": 7.8234,
            "mae": 5.9123,
            "r2": 0.7456,
            "timestamp": "2026-04-01 10:30"
        },
        {
            "run_id": "previous",
            "rmse": 7.3421,
            "mae": 5.4567,
            "r2": 0.8012,
            "timestamp": "2026-04-03 14:15"
        }
    ]
    
    create_table_artifact(
        key="metrics-comparison",
        table=comparison_data,
        description="Comparison of current model with previous runs"
    )


@task
def create_hyperparameters_table():
    """Crea tabla con los mejores hiperparámetros encontrados."""
    
    hyperparams = [
        {"parameter": "learning_rate", "value": "0.2921", "range": "0.01-0.3"},
        {"parameter": "max_depth", "value": "10", "range": "3-10"},
        {"parameter": "min_child_weight", "value": "1.18", "range": "1-10"},
        {"parameter": "subsample", "value": "0.829", "range": "0.6-1.0"},
        {"parameter": "colsample_bytree", "value": "0.879", "range": "0.6-1.0"},
        {"parameter": "reg_alpha", "value": "0.953", "range": "0.0-1.0"},
        {"parameter": "reg_lambda", "value": "0.274", "range": "0.0-1.0"},
    ]
    
    create_table_artifact(
        key="best-hyperparameters",
        table=hyperparams,
        description="Best hyperparameters found by Optuna optimization"
    )


@task
def create_model_links():
    """Crea links a recursos relacionados con el modelo."""
    
    # Link a MLflow (simulado)
    create_link_artifact(
        key="mlflow-experiment",
        link="http://localhost:5000/#/experiments/1",
        link_text="View in MLflow",
        description="MLflow experiment tracking for this run"
    )
    
    # Link a modelo guardado (simulado)
    create_link_artifact(
        key="model-artifact",
        link="s3://ml-models/nyc-taxi/model-2026-04-05.pkl",
        link_text="Download Model",
        description="Trained model artifact in S3"
    )
    
    # Link a dataset (simulado)
    create_link_artifact(
        key="training-data",
        link="s3://ml-data/nyc-taxi/train-2025-01.parquet",
        link_text="Training Dataset",
        description="Dataset used for training"
    )


@task
def create_feature_importance_table():
    """Crea tabla con importancia de features."""
    
    # Simular top 10 features más importantes
    features = [
        {"feature": "PULocationID_161", "importance": 0.1234},
        {"feature": "DOLocationID_237", "importance": 0.0987},
        {"feature": "PULocationID_230", "importance": 0.0856},
        {"feature": "trip_distance", "importance": 0.0745},
        {"feature": "DOLocationID_161", "importance": 0.0698},
        {"feature": "PULocationID_236", "importance": 0.0623},
        {"feature": "hour_of_day", "importance": 0.0587},
        {"feature": "day_of_week", "importance": 0.0534},
        {"feature": "DOLocationID_236", "importance": 0.0489},
        {"feature": "PULocationID_138", "importance": 0.0445},
    ]
    
    create_table_artifact(
        key="feature-importance",
        table=features,
        description="Top 10 most important features for the model"
    )


@task
def create_validation_results():
    """Crea resumen de validación del modelo."""
    
    markdown_content = """
# 🎯 Model Validation Results

## Data Quality Checks

| Check | Status | Details |
|-------|--------|---------|
| Null Values | ✅ Pass | < 10% threshold |
| Sample Size | ✅ Pass | 46,307 records |
| Feature Count | ✅ Pass | 448 features |
| Target Distribution | ✅ Pass | Normal distribution |

## Performance on Validation Set

- **RMSE**: 7.15 minutes
- **MAE**: 5.23 minutes
- **Within 5 min**: 68.5% of predictions
- **Within 10 min**: 89.2% of predictions

## Comparison with Baseline

| Metric | Current | Baseline | Improvement |
|--------|---------|----------|-------------|
| RMSE | 7.15 | 7.82 | 🟢 8.6% |
| MAE | 5.23 | 5.91 | 🟢 11.5% |
| R² | 0.823 | 0.746 | 🟢 10.3% |

## Recommendation

✅ **APPROVED FOR DEPLOYMENT**

Model shows consistent improvement over baseline across all metrics.
Ready for A/B testing in production.
"""
    
    create_markdown_artifact(
        key="validation-results",
        markdown=markdown_content,
        description="Complete validation results and deployment recommendation"
    )


@flow(name="ml-artifacts-demo", log_prints=True)
def ml_artifacts_flow():
    """
    Flow que demuestra el uso de artifacts para ML workflows.
    
    Ejecuta este flow y ve los artifacts en Prefect Cloud:
    - Flow Runs → [tu run] → Artifacts tab
    """
    logger = get_run_logger()
    
    logger.info("🚀 Starting ML Artifacts Demo")
    
    # 1. Entrenar modelo (simulado)
    metrics = train_model_simulation()
    
    # 2. Crear artifacts de métricas
    logger.info("📊 Creating metrics artifacts...")
    create_metrics_summary(metrics)
    create_metrics_table(metrics)
    
    # 3. Crear tabla de hiperparámetros
    logger.info("⚙️ Creating hyperparameters artifact...")
    create_hyperparameters_table()
    
    # 4. Crear links a recursos
    logger.info("🔗 Creating resource links...")
    create_model_links()
    
    # 5. Crear tabla de feature importance
    logger.info("📈 Creating feature importance artifact...")
    create_feature_importance_table()
    
    # 6. Crear resumen de validación
    logger.info("✅ Creating validation results...")
    create_validation_results()
    
    logger.info("🎉 All artifacts created successfully!")
    logger.info("📱 View them in Prefect Cloud → Flow Runs → Artifacts tab")
    
    return {
        "status": "success",
        "artifacts_created": 7,
        "rmse": metrics['rmse']
    }


if __name__ == "__main__":
    # Ejecutar el flow
    result = ml_artifacts_flow()
    
    print("\n" + "="*60)
    print("✅ Flow completed!")
    print("="*60)
    print(f"\nResult: {result}")
    print("\n📱 Go to Prefect Cloud to see the artifacts:")
    print("   https://app.prefect.cloud")
    print("\n💡 Navigate to:")
    print("   Flow Runs → ml-artifacts-demo → Artifacts tab")
    print("\nYou should see 7 artifacts:")
    print("   1. Model Training Summary (markdown)")
    print("   2. Metrics Comparison (table)")
    print("   3. Best Hyperparameters (table)")
    print("   4. MLflow Experiment (link)")
    print("   5. Model Artifact (link)")
    print("   6. Training Data (link)")
    print("   7. Feature Importance (table)")
    print("   8. Validation Results (markdown)")
