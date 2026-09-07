# Model Registry - Registro del Mejor Modelo

Este documento explica cómo el pipeline registra automáticamente el modelo obtenido mediante optimización con Optuna en el MLflow Model Registry, usando aliases (`champion` / `candidate`) en lugar del sistema de stages, que MLflow tiene deprecado.

## Arquitectura del Sistema

```
Pipeline Flow:
1. Optimización de hiperparámetros (Optuna)
2. Entrenamiento del modelo final (XGBoost)
3. Registro en MLflow Model Registry, con alias "candidate"
4. Comparación de RMSE contra el "champion" actual
5. Promoción a "champion" solo si el nuevo modelo es mejor
```

## Componentes

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
- Le asigna siempre el alias `candidate`
- Compara su RMSE contra el modelo que actualmente tiene el alias `champion`
- Solo si no hay champion todavía, o si el nuevo modelo tiene menor RMSE, le asigna también el alias `champion`
- Crea un artifact en Prefect con el detalle de la comparación
- Retorna el número de versión del modelo

### 2. Integración en Pipeline: `pipeline.py`

El pipeline incluye automáticamente el registro del modelo:

```python
# Entrenar modelo
model_run_id, rmse = train_model(X_train, y_train, X_val, y_val, dv, best_params)

# Registrar en Model Registry (candidate siempre, champion solo si mejora)
model_version = register_best_model(
    run_id=model_run_id,
    rmse=rmse,
    model_name="nyc-taxi-duration-predictor"
)
```

## Uso

### Ejecutar Pipeline Completo

```bash
# Ejecutar pipeline (entrena y registra automaticamente)
python pipeline.py --year 2025 --month 1

# El pipeline:
# 1. Optimiza hiperparámetros con Optuna
# 2. Entrena el mejor modelo
# 3. Lo registra en MLflow Model Registry (candidate, y champion si mejora)
```

### Verificar Modelo Registrado

```bash
# Iniciar MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Navegar a: http://localhost:5000/#/models/nyc-taxi-duration-predictor
```

## Información del Modelo Registrado

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

### Aliases
- `candidate`: se asigna a **toda** versión nueva registrada
- `champion`: se asigna solo si esa versión mejora el RMSE del champion actual (o si es la primera versión)

### Artifacts
- Modelo XGBoost entrenado
- Preprocessor (DictVectorizer)
- Métricas de entrenamiento

## Siguiente Paso: Deployment

Una ver registrado el modelo, puedes:

### 1. Consultar cuál es el champion actual

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

champion = client.get_model_version_by_alias("nyc-taxi-duration-predictor", "champion")
print(champion.version, champion.tags.get("rmse"))
```

### 2. Cargar el Modelo Champion para Deployment

```python
import mlflow

# Siempre carga la version que tenga el alias "champion" en este momento
model_uri = "models:/nyc-taxi-duration-predictor@champion"
model = mlflow.xgboost.load_model(model_uri)

# Hacer predicciones
predictions = model.predict(data)
```

### 3. Usar en Módulo de Deployment

El modelo champion estará disponible para:
- APIs REST (FastAPI, Flask)
- Batch predictions
- Streaming predictions
- Deployment en cloud (AWS, GCP, Azure)

## Estructura de Archivos

```
Prefect-pipelines/
├── pipeline.py                          # Pipeline principal (incluye registro)
├── src/
│   └── models/
│       ├── optimization.py             # Optuna + entrenamiento
│       ├── model_registry.py            # Registro en MLflow (alias-based)
│       └── __init__.py                  # Exports
├── models/
│   └── preprocessor.b                   # Backup local del preprocessor
└── mlruns/                              # Artifacts de MLflow
```

## Ejemplo de Salida del Pipeline

```
Starting hyperparameter optimization...
Best trial was trial_12 with RMSE: 6.2345

Training final model with optimized parameters...
Model logged successfully to MLflow

Registering best model in MLflow Model Registry...
Model registered successfully as 'nyc-taxi-duration-predictor' version 3
Model version 3 tagged with metadata
Version 3 (RMSE 6.2345) improves on the current champion (RMSE 6.5012). Promoted to 'champion'.

Pipeline completed successfully!
MLflow run_id: abc123def456
Model registered in MLflow Model Registry: nyc-taxi-duration-predictor
```

Si la versión nueva **no** mejora al champion, el pipeline igual termina con éxito: el modelo queda registrado con el alias `candidate`, disponible para revisión, pero el `champion` no cambia. Así ninguna corrida degrada el modelo que está en producción.

## Ventajas de este Enfoque

1. **Versionamiento**: Cada ejecución crea una nueva versión
2. **Trazabilidad**: Conexión directa con el run de entrenamiento
3. **Metadata**: Tags y descripciones para búsqueda fácil
4. **Seguridad**: el champion solo cambia si el modelo nuevo es objetivamente mejor
5. **Deployment**: URI único (`models:/<nombre>@champion`) que siempre apunta al mejor modelo vigente
6. **Comparación**: Comparar versiones fácilmente por sus tags de RMSE

## Referencias

- **MLflow Model Registry**: https://mlflow.org/docs/latest/model-registry.html
- **MLflow Model Aliases** (reemplazan a los stages): https://mlflow.org/docs/latest/model-registry.html#model-registry-workflows
- **Prefect Tasks**: https://docs.prefect.io/concepts/tasks/
- **XGBoost**: https://xgboost.readthedocs.io/

## Notas Importantes

- El modelo se registra **automáticamente** después del entrenamiento, sin intervención manual
- Toda versión nueva recibe el alias `candidate`
- El alias `champion` solo se reasigna cuando el RMSE de la nueva versión es menor que el del champion actual (o cuando todavía no existe un champion)
- El sistema de stages (`None` / `Staging` / `Production` / `Archived`) está deprecado en MLflow; por eso este módulo usa aliases en su lugar
- Cada ejecución del pipeline crea una nueva versión del modelo, pero **no** todas se convierten en champion
