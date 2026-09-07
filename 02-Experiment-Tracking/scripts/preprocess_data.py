"""Descarga y preprocesa el dataset de viajes en taxi verde de NYC.

Este script:
1. Descarga los archivos parquet de enero y febrero de 2023 (si no existen ya
   en disco, para no volver a descargar cada vez que se ejecuta).
2. Calcula la variable objetivo `duration` (minutos) y filtra outliers.
3. Vectoriza las columnas categoricas y numericas con un DictVectorizer.
4. Guarda los artefactos (`X_train`, `y_train`, `X_val`, `y_val`, `dv`) listos
   para ser usados por los scripts de entrenamiento.
"""

import logging
import os
import pickle
import urllib.request

import pandas as pd
from sklearn.feature_extraction import DictVectorizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

CATEGORICAL = ["PULocationID", "DOLocationID"]
NUMERICAL = ["trip_distance"]
TARGET = "duration"


def download_data(url: str, filename: str) -> None:
    """Descarga un archivo desde `url` y lo guarda en `filename`.

    Si el archivo ya existe, no se vuelve a descargar (evita tráfico y
    tiempo de espera innecesarios en cada ejecución del script).
    """
    if os.path.exists(filename):
        logger.info("Archivo %s ya existe, se omite la descarga.", filename)
        return

    logger.info("Descargando %s en %s ...", url, filename)
    try:
        urllib.request.urlretrieve(url, filename)
        logger.info("Descarga completada: %s", filename)
    except Exception:
        logger.exception("Error descargando %s", filename)
        raise


def add_duration_column(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula la duración del viaje en minutos y filtra valores atípicos.

    Se conservan únicamente los viajes entre 1 y 60 minutos, que es el
    rango típico usado en este curso para evitar outliers extremos
    (viajes de segundos o de varias horas por errores de registro).
    """
    df = df.copy()
    df["duration"] = df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]
    df["duration"] = df["duration"].apply(lambda td: td.total_seconds() / 60)
    df = df[(df["duration"] >= 1) & (df["duration"] <= 60)]
    return df


def preprocess_data(data_path: str, output_path: str) -> None:
    """Descarga, limpia y vectoriza el dataset, y guarda los artefactos resultantes."""
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)

    jan_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-01.parquet"
    feb_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-02.parquet"

    jan_path = os.path.join(data_path, "jan.parquet")
    feb_path = os.path.join(data_path, "feb.parquet")

    download_data(jan_url, jan_path)
    download_data(feb_url, feb_path)

    logger.info("Cargando datos crudos en memoria...")
    df_train = pd.read_parquet(jan_path)
    df_val = pd.read_parquet(feb_path)

    logger.info("Calculando duración y filtrando outliers...")
    df_train = add_duration_column(df_train)
    df_val = add_duration_column(df_val)

    df_train[CATEGORICAL] = df_train[CATEGORICAL].astype(str)
    df_val[CATEGORICAL] = df_val[CATEGORICAL].astype(str)

    logger.info("Vectorizando features (%s registros de train, %s de validación)...",
                len(df_train), len(df_val))
    train_dicts = df_train[CATEGORICAL + NUMERICAL].to_dict(orient="records")
    val_dicts = df_val[CATEGORICAL + NUMERICAL].to_dict(orient="records")

    dv = DictVectorizer()
    x_train = dv.fit_transform(train_dicts)
    x_val = dv.transform(val_dicts)

    y_train = df_train[TARGET].values
    y_val = df_val[TARGET].values

    artifacts = {
        "X_train.pkl": x_train,
        "y_train.pkl": y_train,
        "X_val.pkl": x_val,
        "y_val.pkl": y_val,
        "dv.pkl": dv,
    }
    for filename, obj in artifacts.items():
        path = os.path.join(output_path, filename)
        with open(path, "wb") as f_out:
            pickle.dump(obj, f_out)
        logger.info("Guardado: %s", path)

    logger.info("Preprocesamiento finalizado correctamente.")


if __name__ == "__main__":
    preprocess_data(data_path="data", output_path="data/processed")
