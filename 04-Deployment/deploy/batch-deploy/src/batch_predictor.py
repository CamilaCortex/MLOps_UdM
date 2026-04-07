"""
Batch predictor usando modelo local copiado del pipeline.
Versión simplificada que carga modelo desde archivos locales.
"""

import pickle
import pandas as pd
import mlflow
import xgboost as xgb
from datetime import datetime
import json
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings
from src.database import get_database

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def load_local_model():
    """
    Carga modelo y preprocessor desde archivos locales.
    
    Returns:
        Tuple of (preprocessor, model, metadata)
    """
    model_dir = settings.MODEL_DIR
    
    logging.info(f"Cargando modelo local desde: {model_dir}")
    
    # Verificar que existe el directorio
    if not model_dir.exists():
        raise FileNotFoundError(
            f"Directorio del modelo no encontrado: {model_dir}\n"
            f"Ejecuta primero: python copy_model.py"
        )
    
    # Cargar metadata
    metadata_file = model_dir / "metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata no encontrada: {metadata_file}")
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    logging.info(f"Modelo: {metadata['model_name']} v{metadata['version']}")
    logging.info(f"RMSE: {metadata['rmse']:.4f}")
    
    # Cargar modelo XGBoost
    model_path = model_dir / "models_mlflow"
    if not model_path.exists():
        raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
    
    model = mlflow.xgboost.load_model(str(model_path))
    
    # Cargar preprocessor
    preprocessor_file = model_dir / "preprocessor" / "preprocessor.b"
    if not preprocessor_file.exists():
        raise FileNotFoundError(f"Preprocessor no encontrado: {preprocessor_file}")
    
    with open(preprocessor_file, 'rb') as f:
        preprocessor = pickle.load(f)
    
    logging.info("Modelo y preprocessor cargados exitosamente")
    
    return preprocessor, model, metadata


def prepare_features(df):
    """
    Prepara features para predicción.
    
    Args:
        df: DataFrame con datos de viajes
        
    Returns:
        List of feature dictionaries
    """
    logging.info(f"Preparando features para {len(df)} viajes...")
    
    features = []
    for _, row in df.iterrows():
        feature = {
            'PU_DO': f"{int(row['PULocationID'])}_{int(row['DOLocationID'])}",
            'trip_distance': float(row['trip_distance'])
        }
        features.append(feature)
    
    logging.info("Features preparadas")
    return features


def make_predictions(features, dv, model):
    """
    Hace predicciones batch.
    
    Args:
        features: List of feature dictionaries
        dv: DictVectorizer preprocessor
        model: Trained XGBoost model
        
    Returns:
        Array of predictions
    """
    logging.info(f"Haciendo {len(features)} predicciones...")
    
    start_time = datetime.now()
    
    # Transformar features
    X = dv.transform(features)
    
    # Convertir a DMatrix para XGBoost 3.x
    dmatrix = xgb.DMatrix(X)
    predictions = model.predict(dmatrix)
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    logging.info(f"Predicciones completadas en {processing_time:.2f} segundos")
    logging.info(f"Velocidad: {len(predictions)/processing_time:.0f} predicciones/segundo")
    
    return predictions


def save_predictions_to_db(df, predictions, metadata, batch_id=None):
    """
    Guarda predicciones en base de datos SQL.
    
    Args:
        df: DataFrame con input features
        predictions: Array of predictions
        metadata: Dictionary con metadata del modelo
        batch_id: Optional batch identifier
        
    Returns:
        Number of records saved
    """
    if batch_id is None:
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logging.info("Guardando predicciones en base de datos...")
    
    # Preparar model_info para la base de datos
    model_info = {
        'name': metadata['model_name'],
        'version': str(metadata['version']),
        'stage': 'Production',  # Asumimos Production
        'run_id': metadata.get('run_id', 'local')
    }
    
    # Guardar en base de datos
    db = get_database()
    num_saved = db.save_predictions(
        df=df,
        predictions=predictions,
        model_info=model_info,
        batch_id=batch_id
    )
    
    # Estadísticas
    logging.info("Estadísticas de Predicciones:")
    logging.info(f"  Duración Promedio: {predictions.mean():.1f} minutos")
    logging.info(f"  Duración Mínima: {predictions.min():.1f} minutos")
    logging.info(f"  Duración Máxima: {predictions.max():.1f} minutos")
    logging.info(f"  Desviación Estándar: {predictions.std():.1f} minutos")
    
    return num_saved


def process_batch_file(input_file):
    """
    Procesa un archivo batch completo.
    
    Args:
        input_file: Path to input parquet file
        
    Returns:
        Dictionary with processing results
    """
    logging.info("="*60)
    logging.info(f"Procesando archivo batch: {input_file}")
    logging.info("="*60)
    
    # 1. Cargar modelo local
    logging.info("Paso 1: Cargando modelo local")
    dv, model, metadata = load_local_model()
    
    # 2. Leer datos de entrada
    logging.info("Paso 2: Leyendo datos de entrada")
    df = pd.read_parquet(input_file)
    logging.info(f"Cargados {len(df)} viajes")
    
    # 3. Preparar features
    logging.info("Paso 3: Preparando features")
    features = prepare_features(df)
    
    # 4. Hacer predicciones
    logging.info("Paso 4: Haciendo predicciones")
    predictions = make_predictions(features, dv, model)
    
    # 5. Guardar en base de datos
    logging.info("Paso 5: Guardando en base de datos SQL")
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    num_saved = save_predictions_to_db(df, predictions, metadata, batch_id)
    
    # Resumen
    logging.info("="*60)
    logging.info("Procesamiento batch completado exitosamente")
    logging.info("="*60)
    logging.info(f"  Viajes Procesados: {len(df)}")
    logging.info(f"  Registros Guardados: {num_saved}")
    logging.info(f"  Batch ID: {batch_id}")
    logging.info(f"  Modelo: {metadata['model_name']} v{metadata['version']}")
    logging.info(f"  RMSE del Modelo: {metadata['rmse']:.4f}")
    logging.info("="*60)
    
    return {
        'status': 'success',
        'input_file': str(input_file),
        'trips_processed': len(df),
        'records_saved': num_saved,
        'batch_id': batch_id,
        'model_name': metadata['model_name'],
        'model_version': metadata['version'],
        'model_rmse': metadata['rmse'],
        'avg_duration': float(predictions.mean()),
        'min_duration': float(predictions.min()),
        'max_duration': float(predictions.max())
    }


if __name__ == "__main__":
    # Buscar archivos de input
    input_files = list(settings.DATA_INPUT_DIR.glob("*.parquet"))
    
    if not input_files:
        logging.error("No se encontraron archivos de input")
        logging.info("Ejecuta primero: python src/data_generator.py")
    else:
        # Procesar el archivo más reciente
        latest_file = max(input_files, key=lambda x: x.stat().st_mtime)
        result = process_batch_file(latest_file)
        logging.info("Procesamiento completado")
