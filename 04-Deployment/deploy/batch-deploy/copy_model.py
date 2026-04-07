"""
Script para copiar el modelo más reciente del pipeline a batch-deploy.
Compatible con Mac, Linux y Windows.
"""

import shutil
from pathlib import Path
import json
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def copy_latest_model():
    """
    Copia el modelo más reciente del pipeline a batch-deploy.
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

    # Ordenar por fecha de modificación (más reciente primero)
    latest_model = max(model_dirs, key=lambda d: d.stat().st_mtime)

    logging.info(f"Modelo más reciente: {latest_model.name}")

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
