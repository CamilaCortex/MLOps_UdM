"""
Script para copiar modelo del pipeline a web-service.
"""

import shutil
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def copy_model_to_webservice():
    """Copia el último modelo del pipeline a web-service"""
    
    # Rutas
    project_root = Path(__file__).parent.parent.parent.parent
    # Copiar desde batch-deploy que ya tiene el modelo
    batch_deploy_model = project_root / "04-Deployment" / "deploy" / "batch-deploy" / "model"
    webservice_model = Path(__file__).parent / "model"
    
    logging.info("Copiando modelo de batch-deploy a web-service...")
    logging.info("Origen: %s", batch_deploy_model)
    logging.info("Destino: %s", webservice_model)
    
    # Verificar que existe el modelo en batch-deploy
    if not batch_deploy_model.exists():
        raise FileNotFoundError(
            f"Modelo no encontrado en: {batch_deploy_model}\n"
            "Ejecuta primero en batch-deploy: uv run python copy_model.py"
        )
    
    # Leer metadata
    metadata_file = batch_deploy_model / "metadata.json"
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    logging.info("Modelo: %s v%s", metadata['model_name'], metadata['version'])
    logging.info("RMSE: %.4f", metadata['rmse'])
    
    # Limpiar destino si existe
    if webservice_model.exists():
        shutil.rmtree(webservice_model)
    
    # Copiar modelo completo
    shutil.copytree(batch_deploy_model, webservice_model)
    
    logging.info("Modelo copiado exitosamente")
    logging.info(f"Archivos copiados:")
    logging.info(f"  - models_mlflow/ (modelo XGBoost)")
    logging.info(f"  - preprocessor/ (DictVectorizer)")
    logging.info(f"  - metadata.json")
    
    return metadata


if __name__ == "__main__":
    metadata = copy_model_to_webservice()
    logging.info("Listo para iniciar web service")
