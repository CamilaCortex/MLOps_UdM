"""Entrenamiento SIN tracking de experimentos (línea base).

Este script existe a proposito para mostrar el problema que resuelve
MLflow: aqui no queda ningun registro de que hiperparametros se usaron
ni de como se llego al RMSE reportado. Si se pierde esta terminal, se
pierde la trazabilidad completa del experimento.

Comparar con `train_with_basic_mlflow.py` para ver la diferencia.
"""

import logging
import os
import pickle

import click
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


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
    logger.info("Entrenando RandomForestRegressor (max_depth=%s)...", max_depth)
    rf = RandomForestRegressor(max_depth=max_depth, random_state=0)
    rf.fit(x_train, y_train)
    y_pred = rf.predict(x_val)

    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
    logger.info("RMSE: %.4f", rmse)
    logger.warning(
        "Este resultado no quedo registrado en ningun lado. "
        "Si cierras la terminal, se pierde."
    )


if __name__ == "__main__":
    run_train()
