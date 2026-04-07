# Model Registry - Registro del Mejor Modelo

Este documento explica cómo el pipeline registra automáticamente el mejor modelo obtenido mediante optimización con Optuna en MLflow Model Registry.

## 📋 Arquitectura del Sistema

```
Pipeline Flow:
1. Optimización de hiperparámetros (Optuna)
2. Entrenamiento del modelo final (XGBoost)
3. Registro en MLflow Model Registry ← NUEVO
4. Disponible para deployment
```

## 🔧 Componentes

### 1. Módulo de Registro: `src/models/model_registry.py`

**Tarea Principal:** `register_best_model`

```python
from src.models import register_best_model

# Registrar modelo en MLflow Model Registry
model_version = register_best_model(
    run_id="mlflow_run_id",
    rmse=6.23,
    model_name="nyc-taxi-duration-predictor"
)
```

**Funcionalidad:**
- Registra el modelo entrenado en MLflow Model Registry
- Agrega metadata (RMSE, tipo de modelo, framework)
- Crea artifact en Prefect con detalles del registro
- Retorna el número de versión del modelo

### 2. Integración en Pipeline: `pipeline.py`

El pipeline ahora incluye automáticamente el registro del modelo:

```python
# Entrenar modelo
model_run_id, rmse = train_model(X_train, y_train, X_val, y_val, dv, best_params)

# Registrar automáticamente en Model Registry
model_version = register_best_model(
    run_id=model_run_id,
    rmse=rmse,
    model_name="nyc-taxi-duration-predictor"
)
```

## 🚀 Uso

### Ejecutar Pipeline Completo

```bash
# Ejecutar pipeline (entrena y registra automáticamente)
python pipeline.py --year 2025 --month 1

# El pipeline:
# 1. Optimiza hiperparámetros con Optuna
# 2. Entrena el mejor modelo
# 3. Registra el modelo en MLflow Model Registry ✅
```

### Verificar Modelo Registrado

```bash
# Iniciar MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Navegar a: http://localhost:5000/#/models/nyc-taxi-duration-predictor
```

## 📊 Información del Modelo Registrado

Cada modelo registrado incluye:

### Metadata
- **Nombre**: `nyc-taxi-duration-predictor`
- **Versión**: Incrementa automáticamente (1, 2, 3, ...)
- **RMSE**: Métrica de rendimiento
- **Descripción**: Detalles del modelo y optimización

### Tags
- `rmse`: Valor de RMSE
- `model_type`: xgboost
- `framework`: prefect+mlflow
- `optimization`: optuna

### Artifacts
- Modelo XGBoost entrenado
- Preprocessor (DictVectorizer)
- Métricas de entrenamiento

## 🎯 Siguiente Paso: Deployment

Una vez registrado el modelo, puedes:

### 1. Transicionar a Staging/Production

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Promover a Production
client.transition_model_version_stage(
    name="nyc-taxi-duration-predictor",
    version="1",
    stage="Production"
)
```

### 2. Cargar Modelo para Deployment

```python
import mlflow

# Cargar modelo desde Production
model_uri = "models:/nyc-taxi-duration-predictor/Production"
model = mlflow.xgboost.load_model(model_uri)

# Hacer predicciones
predictions = model.predict(data)
```

### 3. Usar en Módulo de Deployment

El modelo registrado estará disponible para:
- APIs REST (FastAPI, Flask)
- Batch predictions
- Streaming predictions
- Deployment en cloud (AWS, GCP, Azure)

## 📁 Estructura de Archivos

```
Prefect-pipelines/
├── pipeline.py                          # Pipeline principal (incluye registro)
├── src/
│   └── models/
│       ├── optimization.py              # Optuna + entrenamiento
│       ├── model_registry.py            # Registro en MLflow ← NUEVO
│       └── __init__.py                  # Exports
├── models/
│   └── preprocessor.b                   # Backup local del preprocessor
└── mlruns/                              # Artifacts de MLflow
```

## 🔍 Ejemplo de Salida del Pipeline

```
Starting hyperparameter optimization...
Best trial was trial_12 with RMSE: 6.2345

Training final model with optimized parameters...
✅ Model logged successfully to MLflow

Registering best model in MLflow Model Registry...
✅ Model registered successfully as 'nyc-taxi-duration-predictor' version 3
Model version 3 tagged with metadata

Pipeline completed successfully!
MLflow run_id: abc123def456
Model registered in MLflow Model Registry: nyc-taxi-duration-predictor
```

## 🎓 Ventajas del Model Registry

1. **Versionamiento**: Cada ejecución crea una nueva versión
2. **Trazabilidad**: Conexión directa con el run de entrenamiento
3. **Metadata**: Tags y descripciones para búsqueda fácil
4. **Stages**: Staging → Production workflow
5. **Deployment**: URI único para cargar modelos
6. **Comparación**: Comparar versiones fácilmente

## 🔗 Referencias

- **MLflow Model Registry**: https://mlflow.org/docs/latest/model-registry.html
- **Prefect Tasks**: https://docs.prefect.io/concepts/tasks/
- **XGBoost**: https://xgboost.readthedocs.io/

## ⚠️ Notas Importantes

- El modelo se registra **automáticamente** después del entrenamiento
- No necesitas intervención manual para el registro
- El modelo queda en stage "None" por defecto
- Debes promoverlo manualmente a "Staging" o "Production"
- Cada ejecución del pipeline crea una nueva versión del modelo
