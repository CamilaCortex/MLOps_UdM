"""
Model optimization and training tasks.
"""

import pickle
from pathlib import Path
from typing import Tuple, Dict

import xgboost as xgb
import optuna
import mlflow
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
from prefect import task, get_run_logger
from prefect.artifacts import create_table_artifact, create_markdown_artifact

from .config import OPTUNA_TRIALS


@task(name="optimize_hyperparameters", description="Optimize XGBoost hyperparameters using Optuna")
def optimize_hyperparameters(X_train, y_train, X_val, y_val) -> Dict:
    """
    Optimize XGBoost hyperparameters using Optuna.
    
    Args:
        X_train: Training features
        y_train: Training targets
        X_val: Validation features
        y_val: Validation targets
    
    Returns:
        Dictionary with best hyperparameters
    """
    logger = get_run_logger()
    
    n_trials = OPTUNA_TRIALS
    logger.info(f"Starting hyperparameter optimization with {n_trials} trials...")
    
    def objective(trial):
        """Optuna objective function."""
        params = {
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'min_child_weight': trial.suggest_float('min_child_weight', 1, 10),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 1.0),
            'objective': 'reg:squarederror',
            'seed': 42
        }
        
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)
        
        model = xgb.train(
            params,
            dtrain,
            num_boost_round=100,
            evals=[(dval, 'validation')],
            early_stopping_rounds=10,
            verbose_eval=False
        )
        
        preds = model.predict(dval)
        rmse = root_mean_squared_error(y_val, preds)
        
        return rmse
    
    # Create Optuna study
    study = optuna.create_study(direction='minimize', study_name='xgboost-optimization')
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    best_params = study.best_params
    best_params['objective'] = 'reg:squarederror'
    best_params['seed'] = 42
    
    logger.info("Optimization completed")
    logger.info(f"Best RMSE: {study.best_value:.4f}")
    logger.info(f"Best parameters: {best_params}")
    
    # Create artifact with optimization results
    optimization_data = [
        ["Best RMSE", f"{study.best_value:.4f}"],
        ["Number of Trials", n_trials],
        ["Best Trial", study.best_trial.number],
        ["Learning Rate", f"{best_params['learning_rate']:.6f}"],
        ["Max Depth", best_params['max_depth']],
        ["Min Child Weight", f"{best_params['min_child_weight']:.4f}"],
        ["Subsample", f"{best_params['subsample']:.4f}"],
        ["Colsample Bytree", f"{best_params['colsample_bytree']:.4f}"],
        ["Reg Alpha", f"{best_params['reg_alpha']:.4f}"],
        ["Reg Lambda", f"{best_params['reg_lambda']:.4f}"]
    ]
    
    create_table_artifact(
        key="optuna-optimization",
        table=optimization_data,
        description=f"Optuna optimization results - Best RMSE: {study.best_value:.4f}"
    )
    
    # Create markdown with optimization history
    trials_info = "\n".join([
        f"- Trial {t.number}: RMSE = {t.value:.4f}"
        for t in sorted(study.trials, key=lambda x: x.value)[:5]
    ])
    
    optimization_summary = f"""
    # Hyperparameter Optimization Results
    
    ## Best Performance
    - **Best RMSE**: {study.best_value:.4f}
    - **Best Trial**: #{study.best_trial.number}
    - **Total Trials**: {n_trials}
    
    ## Optimized Parameters
    - Learning Rate: {best_params['learning_rate']:.6f}
    - Max Depth: {best_params['max_depth']}
    - Min Child Weight: {best_params['min_child_weight']:.4f}
    - Subsample: {best_params['subsample']:.4f}
    - Colsample Bytree: {best_params['colsample_bytree']:.4f}
    - Reg Alpha: {best_params['reg_alpha']:.4f}
    - Reg Lambda: {best_params['reg_lambda']:.4f}
    
    ## Top 5 Trials
    {trials_info}
    """
    
    create_markdown_artifact(
        key="optimization-summary",
        markdown=optimization_summary,
        description="Detailed optimization summary"
    )
    
    return best_params


@task(name="train_model", description="Train XGBoost model with MLflow tracking", retries=2)
def train_model(X_train, y_train, X_val, y_val, dv: DictVectorizer, best_params: Dict) -> Tuple[str, float]:
    """
    Train XGBoost model and log to MLflow.

    Args:
        X_train: Training features
        y_train: Training targets
        X_val: Validation features
        y_val: Validation targets
        dv: Fitted DictVectorizer
        best_params: Optimized hyperparameters

    Returns:
        Tuple of (MLflow run_id, RMSE)
    """
    logger = get_run_logger()
    
    # Ensure models directory exists
    models_folder = Path('models')
    models_folder.mkdir(exist_ok=True)
    
    logger.info(f"Training with {X_train.shape[0]} samples, {X_train.shape[1]} features")

    with mlflow.start_run() as run:
        train = xgb.DMatrix(X_train, label=y_train)
        valid = xgb.DMatrix(X_val, label=y_val)

        logger.info(f"Training with optimized hyperparameters: {best_params}")

        mlflow.log_params(best_params)

        booster = xgb.train(
            params=best_params,
            dtrain=train,
            num_boost_round=30,
            evals=[(valid, 'validation')],
            early_stopping_rounds=50
        )

        y_pred = booster.predict(valid)
        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("rmse", rmse)
        
        # Log RMSE without comparison
        previous_best_rmse = None
        improvement = None

        # Save preprocessor
        preprocessor_path = "models/preprocessor.b"
        with open(preprocessor_path, "wb") as f_out:
            pickle.dump(dv, f_out)
        
        try:
            mlflow.log_artifact(preprocessor_path, artifact_path="preprocessor")
            # Log model using updated parameter name
            mlflow.xgboost.log_model(booster, "models_mlflow")
            logger.info("Successfully logged model and preprocessor to MLflow")
        except Exception as e:
            logger.warning(f"Failed to log to MLflow: {e}")
            logger.info("Model artifacts saved locally in models/ directory")

        # Create Prefect artifact with model performance
        performance_data = [
            ["RMSE", f"{rmse:.4f}"],
            ["Learning Rate", best_params['learning_rate']],
            ["Max Depth", best_params['max_depth']],
            ["Num Boost Rounds", 30],
            ["MLflow Run ID", run.info.run_id]
        ]

        create_table_artifact(
            key="model-performance",
            table=performance_data,
            description=f"Model performance metrics - RMSE: {rmse:.4f}"
        )

        # Create enhanced markdown artifact with comparison
        comparison_section = ""
        if previous_best_rmse is not None:
            comparison_section = f"""
        ## Performance Comparison
        - **Current RMSE**: {rmse:.4f}
        - **Previous Best**: {previous_best_rmse:.4f}
        - **Improvement**: {improvement:+.2f}%
        - **Status**: {'NEW BEST' if rmse < previous_best_rmse else 'Not improved'}
        """
        
        mlflow_ui_url = mlflow.get_tracking_uri().replace('sqlite:///', 'http://localhost:5000/')
        
        markdown_content = f"""
        # Model Training Summary

        ## Performance
        - **RMSE**: {rmse:.4f}
        - **MLflow Run ID**: [{run.info.run_id}]({mlflow_ui_url})

        {comparison_section}

        ## Model Configuration
        - **Learning Rate**: {best_params['learning_rate']:.6f}
        - **Max Depth**: {best_params['max_depth']}
        - **Num Boost Rounds**: 30

        ## Artifacts
        - Model saved to MLflow
        - Preprocessor saved to MLflow
        - Local backup in `models/` directory
        """

        create_markdown_artifact(
            key="training-summary",
            markdown=markdown_content,
            description="Complete training summary with performance metrics"
        )

        return run.info.run_id, rmse
