"""
Simple example of Prefect Artifacts for ML workflows.

Artifacts allow you to visualize results and metrics directly in Prefect Cloud.
"""

from prefect import flow, task, get_run_logger
from prefect.artifacts import create_markdown_artifact, create_table_artifact
from datetime import datetime


@task
def train_model():
    """Simulate model training and return metrics."""
    logger = get_run_logger()
    logger.info("Training model")
    
    metrics = {
        "rmse": 7.15,
        "mae": 5.23,
        "r2": 0.82,
        "training_time": 45.2
    }
    
    return metrics


@task
def create_summary_artifact(metrics: dict):
    """Create a markdown artifact with training summary."""
    
    markdown_content = f"""
# Model Training Summary

## Performance Metrics

| Metric | Value |
|--------|-------|
| RMSE | {metrics['rmse']:.2f} |
| MAE | {metrics['mae']:.2f} |
| R2 Score | {metrics['r2']:.2f} |

## Training Details

- Training Time: {metrics['training_time']:.1f} seconds
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Status: Model trained successfully
"""
    
    create_markdown_artifact(
        key="training-summary",
        markdown=markdown_content,
        description="Model training summary"
    )


@task
def create_comparison_artifact(metrics: dict):
    """Create a table artifact comparing runs."""
    
    comparison_data = [
        {
            "run": "current",
            "rmse": metrics['rmse'],
            "mae": metrics['mae'],
            "r2": metrics['r2']
        },
        {
            "run": "baseline",
            "rmse": 7.82,
            "mae": 5.91,
            "r2": 0.75
        }
    ]
    
    create_table_artifact(
        key="metrics-comparison",
        table=comparison_data,
        description="Comparison with baseline"
    )


@flow(name="artifacts-example")
def artifacts_flow():
    """
    Flow demonstrating artifact creation.
    
    Run this flow and view artifacts in Prefect Cloud:
    Flow Runs -> [your run] -> Artifacts tab
    """
    logger = get_run_logger()
    logger.info("Starting artifacts example")
    
    # Train model
    metrics = train_model()
    
    # Create artifacts
    create_summary_artifact(metrics)
    create_comparison_artifact(metrics)
    
    logger.info("Artifacts created successfully")
    
    return {"status": "success", "rmse": metrics['rmse']}


if __name__ == "__main__":
    result = artifacts_flow()
    
    print("\nFlow completed")
    print(f"Result: {result}")
    print("\nView artifacts in Prefect Cloud:")
    print("  Flow Runs -> artifacts-example -> Artifacts tab")
