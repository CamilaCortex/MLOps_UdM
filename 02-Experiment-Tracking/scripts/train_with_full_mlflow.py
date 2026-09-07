"""Optimizacion de hiperparametros (Optuna) con tracking completo en MLflow.

Cada trial de Optuna se registra como un run independiente en MLflow, con
sus hiperparametros y su RMSE de validacion. Al final se reporta el mejor
trial encontrado.

Requiere tener un MLflow Tracking Server corriendo en
http://127.0.0.1:5000 (ver README.md del modulo).
"""

import logging
import os
import pickle

import click
import mlflow
import numpy as np
import optuna
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "nyc-taxi-experiment-hpo"
N_TRIALS = 10

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)


def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./data/processed",
    help="Ubicación de los datos preprocesados de NYC taxi trip.",
)
def run_optimization(data_path: str) -> None:
    logger.info("Tracking URI: %s | Experimento: %s", TRACKING_URI, EXPERIMENT_NAME)
    logger.info("Cargando datos preprocesados desde %s", data_path)

    x_train, y_train = (
        load_pickle(os.path.join(data_path, "X_train.pkl")),
        load_pickle(os.path.join(data_path, "y_train.pkl")),
    )
    x_val, y_val = (
        load_pickle(os.path.join(data_path, "X_val.pkl")),
        load_pickle(os.path.join(data_path, "y_val.pkl")),
    )

    def objective(trial: optuna.Trial) -> float:
        with mlflow.start_run():
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 10, 50, 1),
                "max_depth": trial.suggest_int("max_depth", 1, 20, 1),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10, 1),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 4, 1),
                "random_state": 42,
                "n_jobs": -1,
            }
            mlflow.log_params(params)

            rf = RandomForestRegressor(**params)
            rf.fit(x_train, y_train)
            y_pred = rf.predict(x_val)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            mlflow.log_metric("rmse", rmse)

        logger.info("Trial %s | rmse=%.4f | params=%s", trial.number, rmse, params)
        return rmse

    sampler = optuna.samplers.TPESampler(seed=42)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(objective, n_trials=N_TRIALS)

    logger.info(
        "Optimizacion finalizada. Mejor RMSE=%.4f con params=%s",
        study.best_value,
        study.best_params,
    )


if __name__ == "__main__":
    run_optimization()
