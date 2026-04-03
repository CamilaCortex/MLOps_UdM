
# Curso MLOps: Seguimiento de Experimentos con MLflow

Este proyecto proporciona una introducción práctica al seguimiento de experimentos con MLflow, utilizando el conjunto de datos de viajes en taxi verde de NYC como ejemplo.

## Estructura del Proyecto

```
.
├── data/
│   └── processed/
├── notebooks/
│   ├── 00_data_preparation.ipynb
│   ├── 01_first_steps_without_tracking.ipynb
│   ├── 02_experiment_tracking_intro.ipynb
│   └── 03_mlflow_advanced.ipynb
├── scripts/
│   ├── preprocess_data.py
│   ├── train_no_mlflow.py
│   ├── train_with_basic_mlflow.py
│   └── train_with_full_mlflow.py
├── mlflow.db
└── README.md
```

* **data/:** Almacena el conjunto de datos crudo y procesado.
* **notebooks/:** Contiene notebooks de Jupyter que explican los conceptos.
* **scripts/:** Contiene los scripts de Python para el preprocesamiento de datos y entrenamiento del modelo.
* **mlflow.db:** Una base de datos SQLite que sirve como servidor de seguimiento de MLflow.

## Comenzando

### 1. Instalación

Este proyecto usa `uv` para la gestión de paquetes. Para instalar las dependencias, ejecuta:

```bash
uv add "pandas" "scikit-learn" "mlflow" "optuna" "numpy" "pyarrow"
```

### 2. Preprocesamiento de Datos

Primero, ejecuta el script de preprocesamiento de datos para descargar el conjunto de datos de viajes en taxi verde de NYC y prepararlo para el entrenamiento:

```bash
uv run python scripts/preprocess_data.py
```

Esto descargará los datos al directorio `data/` y guardará los datos procesados en `data/processed/`.

### 3. Ejecutando los Ejemplos

#### a. Línea Base (Sin Seguimiento de Experimentos)

Para entrenar un modelo sin ningún seguimiento de experimentos, ejecuta:

```bash
uv run python scripts/train_no_mlflow.py
```

Esto entrenará un RandomForestRegressor e imprimirá el RMSE en la consola.

#### b. MLflow Básico

Para entrenar un modelo con seguimiento básico de experimentos de MLflow, ejecuta:

```bash
uv run python scripts/train_with_basic_mlflow.py
```

Esto registrará los parámetros y métricas del modelo en el servidor de seguimiento de MLflow.

#### c. MLflow Avanzado (Optimización de Hiperparámetros)

Para ejecutar optimización de hiperparámetros con Optuna y registrar los resultados en MLflow, ejecuta:

```bash
uv run python scripts/train_with_full_mlflow.py
```

### 4. Visualizando los Resultados en la Interfaz de MLflow

Para ver los resultados de tus experimentos, lanza la interfaz de usuario de MLflow:

```bash
mlflow ui
```

Luego, abre tu navegador web y navega a `http://127.0.0.1:5000`.

## notebooks

El directorio `notebooks/` contiene tres notebooks que proporcionan una explicación más detallada de los conceptos:

* **00_data_preparation.ipynb:** Descarga y preprocesamiento del dataset de taxis NYC.
* **01_first_steps_without_tracking.ipynb:** Entrenamiento de un modelo sin tracking (motiva el "por que").
* **02_experiment_tracking_intro.ipynb:** Introduccion practica a MLflow (logging manual y autolog).
* **03_mlflow_advanced.ipynb:** Optimizacion de hiperparametros con Optuna y Model Registry.
