"""
Cargador del modelo y preprocessor.
"""

import pickle
import json
import mlflow
import xgboost as xgb
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class ModelLoader:
    """Carga y mantiene el modelo en memoria"""
    
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.metadata = None
        self.model_dir = Path(__file__).parent.parent / "model"
    
    def load(self):
        """Carga el modelo y preprocessor"""
        logging.info(f"Cargando modelo desde: {self.model_dir}")
        
        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"Directorio de modelo no encontrado: {self.model_dir}\n"
                "Ejecuta primero: uv run python copy_model.py"
            )
        
        # Cargar metadata
        metadata_file = self.model_dir / "metadata.json"
        with open(metadata_file, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        logging.info(f"Modelo: {self.metadata['model_name']} v{self.metadata['version']}")
        logging.info(f"RMSE: {self.metadata['rmse']:.4f}")
        
        # Cargar modelo XGBoost
        model_path = self.model_dir / "models_mlflow"
        self.model = mlflow.xgboost.load_model(str(model_path))
        
        # Cargar preprocessor
        preprocessor_file = self.model_dir / "preprocessor" / "preprocessor.b"
        with open(preprocessor_file, 'rb') as f:
            self.preprocessor = pickle.load(f)
        
        logging.info("Modelo y preprocessor cargados exitosamente")
    
    def predict(self, features: list) -> list:
        """
        Hace predicciones.
        
        Args:
            features: Lista de diccionarios con features
            
        Returns:
            Lista de predicciones
        """
        if self.model is None or self.preprocessor is None:
            raise RuntimeError("Modelo no cargado. Llama a load() primero.")
        
        # Transformar features
        X = self.preprocessor.transform(features)
        
        # Convertir a DMatrix para XGBoost 3.x
        dmatrix = xgb.DMatrix(X)
        
        # Predecir
        predictions = self.model.predict(dmatrix)
        
        return predictions.tolist()
    
    def is_loaded(self) -> bool:
        """Verifica si el modelo está cargado"""
        return self.model is not None and self.preprocessor is not None


# Instancia global del modelo
model_loader = ModelLoader()
