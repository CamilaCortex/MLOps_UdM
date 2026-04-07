"""Configuración para NYC Taxi Batch Prediction"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_INPUT_DIR = PROJECT_ROOT / "data" / "input"
DATA_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
DB_DIR = PROJECT_ROOT / "data" / "database"

MODEL_DIR = PROJECT_ROOT / "model"

DB_PATH = DB_DIR / "predictions.db"
DB_CONNECTION_STRING = f"sqlite:///{DB_PATH}"

NUM_TRIPS = 1000  # Número de viajes a generar
MAX_WORKERS = 2   # Número de workers para procesamiento paralelo

BATCH_SCHEDULE = "0 */2 * * *"  # Cada 2 horas

COMMON_LOCATIONS = [161, 162, 163, 164, 236, 237, 238, 239, 140, 141, 142, 143]

# Crear directorios si no existen
DATA_INPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)
