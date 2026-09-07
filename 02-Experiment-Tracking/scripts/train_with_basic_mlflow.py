"""Entrenamiento con tracking BASICO de MLflow (params + metrica).

Comparar con `train_no_mlflow.py`: aqui el mismo entrenamiento queda
registrado (parametros e hiperparametros) y se puede consultar despues
en la UI de MLflow, aunque se cierre la terminal.

Requiere tener un MLflow Tracking Server corriendo en
http://127.0.0.1:5000 (ver README.md del modulo).
"""

import logging
import os
import pickle

import click
import mlflow
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "nyc-taxi-experiment"

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
def run_train(data_path: str) -> None:
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

    max_depth = 10
    with mlflow.start_run():
        logger.info("Entrenando RandomForestRegressor (max_depth=%s)...", max_depth)
        rf = RandomForestRegressor(max_depth=max_depth, random_state=0)
        rf.fit(x_train, y_train)
        y_pred = rf.predict(x_val)

        rmse = np.sqrt(mean_squared_error(y_val, y_pred))

        mlflow.log_param("max_depth", max_depth)
        mlflow.log_metric("rmse", rmse)

        logger.info("RMSE: %.4f (registrado en MLflow)", rmse)


if __name__ == "__main__":
    run_train()
