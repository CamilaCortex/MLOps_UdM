"""
Pipeline constants and configuration values.
"""

# Data configuration
DEFAULT_YEAR = 2025
DEFAULT_MONTH = 1
MIN_RECORDS = 1000
NULL_THRESHOLD = 10.0

# Model configuration
OPTUNA_TRIALS = 20
NUM_BOOST_ROUNDS = 30
EARLY_STOPPING_ROUNDS = 50

# MLflow configuration
MLFLOW_EXPERIMENT_NAME = "nyc-taxi-experiment-prefect"
MLFLOW_DEFAULT_URI = "sqlite:///mlflow.db"

# Feature configuration
CATEGORICAL_FEATURES = ['PU_DO', 'trip_distance']  # PU_DO es combinación de PULocationID_DOLocationID
TARGET_COLUMN = 'duration'

# Data quality thresholds
MIN_DURATION = 1
MAX_DURATION = 60
