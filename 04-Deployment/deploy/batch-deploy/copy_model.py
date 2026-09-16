"""
Script para copiar el modelo más reciente del pipeline a batch-deploy.
Compatible con Mac, Linux y Windows.
"""

import shutil
from pathlib import Path
import json
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

MODEL_NAME = "nyc-taxi-duration-predictor"
CHAMPION_ALIAS = "champion"


def _resolve_champion_version(project_root: Path):
    """
    Consulta el MLflow Model Registry y devuelve el numero de version
    (como string) que tiene actualmente el alias "champion".

    Devuelve None si no se pudo conectar a MLflow o si el modelo todavia
    no tiene ningun champion (por ejemplo, antes de la primera corrida del
    pipeline de entrenamiento) - en ese caso el llamador debe usar un
    fallback.
    """
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        from mlflow.exceptions import MlflowException

        try:
            from prefect.blocks.system import Secret
            mlflow_uri = Secret.load("mlflow-tracking-uri").get()
        except Exception:
            pipeline_dir = project_root / "03-Orchestration" / "Prefect-pipelines"
            mlflow_uri = os.getenv(
                "MLFLOW_TRACKING_URI",
                f"sqlite:///{pipeline_dir / 'mlflow.db'}",
            )

        mlflow.set_tracking_uri(mlflow_uri)
        client = MlflowClient()

        champion = client.get_model_version_by_alias(MODEL_NAME, CHAMPION_ALIAS)
        logging.info(
            f"Champion actual en MLflow: {MODEL_NAME} v{champion.version} "
            f"(RMSE={champion.tags.get('rmse', '?')})"
        )
        return str(champion.version)

    except MlflowException as e:
        logging.warning(f"No se encontro un alias '{CHAMPION_ALIAS}' en MLflow: {e}")
        return None
    except Exception as e:
        logging.warning(f"No se pudo consultar MLflow para resolver el champion: {e}")
        return None


def copy_latest_model():
    """
    Copia a batch-deploy el modelo que MLflow tiene marcado como "champion".
    Si por alguna razon no se puede resolver el champion (sin conexion a
    MLflow, o todavia no existe ningun champion), cae de vuelta a copiar la
    carpeta local mas reciente por fecha de modificacion - el comportamiento
    anterior de este script.
    """
    # Obtener directorios
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent

    pipeline_models = (
        project_root
        / "03-Orchestration"
        / "Prefect-pipelines"
        / "models"
        / "registered"
    )
    batch_models = script_dir / "model"

    logging.info("Copiando modelo del pipeline a batch-deploy...")
    logging.info(f"Proyecto raíz: {project_root}")

    # Verificar que existe el directorio de modelos del pipeline
    if not pipeline_models.exists():
        logging.error(f"No se encontró el directorio de modelos: {pipeline_models}")
        logging.info("Asegúrate de haber ejecutado el pipeline primero")
        sys.exit(1)

    # Encontrar el modelo más reciente
    model_dirs = [d for d in pipeline_models.iterdir() if d.is_dir()]

    if not model_dirs:
        logging.error(f"No se encontraron modelos en {pipeline_models}")
        logging.info("Ejecuta primero el pipeline de entrenamiento")
        sys.exit(1)

    # Preferir el modelo marcado como "champion" en el MLflow Model Registry.
    # Cada carpeta local tiene metadata.json con el numero de version que
    # le corresponde (ver _save_model_locally en model_registry.py), asi
    # que buscamos la carpeta cuyo metadata.json coincide con esa version.
    champion_version = _resolve_champion_version(project_root)
    latest_model = None

    if champion_version is not None:
        for d in model_dirs:
            metadata_file = d / "metadata.json"
            if not metadata_file.exists():
                continue
            try:
                with open(metadata_file, "r") as f:
                    version = str(json.load(f).get("version"))
            except Exception:
                continue
            if version == champion_version:
                latest_model = d
                break

        if latest_model is None:
            logging.warning(
                f"El champion es la version {champion_version}, pero no hay "
                f"ninguna carpeta local en {pipeline_models} con esa version "
                f"(¿fallo el guardado local en esa corrida del pipeline?)."
            )

    if latest_model is None:
        # Fallback: comportamiento anterior (carpeta mas reciente por mtime)
        logging.warning(
            "Usando fallback: la carpeta local mas reciente por fecha de "
            "modificacion, que no necesariamente es el champion actual."
        )
        latest_model = max(model_dirs, key=lambda d: d.stat().st_mtime)

    logging.info(f"Modelo seleccionado: {latest_model.name}")

    # Crear directorio de destino
    batch_models.mkdir(parents=True, exist_ok=True)

    # Limpiar modelo anterior si existe
    if batch_models.exists():
        for item in batch_models.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    # Copiar modelo completo
    logging.info("Copiando archivos...")

    for item in latest_model.iterdir():
        dest = batch_models / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    logging.info(f"Modelo copiado exitosamente a: {batch_models}")

    # Mostrar archivos copiados
    logging.info("Archivos copiados:")
    for item in batch_models.iterdir():
        if item.is_dir():
            logging.info(f"  {item.name}/")
        else:
            logging.info(f"  {item.name}")

    # Mostrar metadata
    metadata_file = batch_models / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        logging.info("Metadata del modelo:")
        logging.info(f"  Nombre: {metadata['model_name']}")
        logging.info(f"  Versión: {metadata['version']}")
        logging.info(f"  RMSE: {metadata['rmse']:.4f}")
        logging.info(f"  Timestamp: {metadata['timestamp']}")

    logging.info("Modelo disponible para batch deployment")
    return True


if __name__ == "__main__":
    try:
        copy_latest_model()
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
