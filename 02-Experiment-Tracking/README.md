
# Curso MLOps: Seguimiento de Experimentos con MLflow

Introducción práctica al seguimiento de experimentos (experiment tracking) con MLflow,
usando el dataset de viajes en taxi verde de NYC como ejemplo principal y el dataset
`iris` para los escenarios de arquitectura de MLflow.

## Estructura del Proyecto

```
.
├── README.md
├── notebooks/
│   ├── 00_data_preparation.ipynb              # Descarga y preprocesa los datos
│   ├── 01_first_steps_without_tracking.ipynb  # Entrenamiento SIN tracking (el problema)
│   ├── 02_experiment_tracking_intro.ipynb     # Tracking con MLflow (la solución)
│   ├── 03_mlflow_advanced.ipynb               # Optuna + Model Registry
│   └── data/                                  # Datos crudos y procesados
├── scenarios/
│   ├── scenario-1.ipynb   # MLflow local, sin servidor (ej. Kaggle)
│   ├── scenario-2.ipynb   # Servidor MLflow local + SQLite (equipo pequeño)
│   └── scenario-3.ipynb   # MLflow en AWS: EC2 + RDS + S3 (equipo distribuido)
└── scripts/
    ├── preprocess_data.py
    ├── train_no_mlflow.py
    ├── train_with_basic_mlflow.py
    └── train_with_full_mlflow.py
```

* **notebooks/:** conceptos explicados paso a paso, del problema (sin tracking) a la
  solución (MLflow) y sus features avanzadas (HPO, Model Registry).
* **scenarios/:** tres arquitecturas reales de MLflow, de la más simple a la más
  parecida a producción.
* **scripts/:** versiones "productivas" de los notebooks, pensadas para correr desde
  la terminal (usan `logging` en vez de prints, y son las que se ejecutarían en un
  pipeline real).

## Comenzando

### 1. Instalación

Este módulo usa el entorno de todo el repositorio (`MLOps_UdM`), gestionado con `uv`
desde la raíz del proyecto. Si ya ejecutaste `uv sync` en la raíz, no necesitas instalar
nada adicional: `mlflow`, `optuna`, `scikit-learn`, `xgboost` y `pyarrow` ya están
disponibles en el entorno virtual `.venv`.

```bash
# Desde la raíz del repositorio (MLOps_UdM/)
uv sync
```

### 2. Preprocesamiento de Datos

Ejecuta el script de preprocesamiento para descargar el dataset de taxis verdes de NYC
y dejarlo listo para entrenar (si los archivos ya existen en `data/`, no se vuelven a
descargar):

```bash
cd 02-Experiment-Tracking
uv run python scripts/preprocess_data.py
```

Esto descarga los datos crudos a `data/` y guarda los datos procesados en
`data/processed/`.

### 3. Ejecutando los Ejemplos

#### a. Línea Base (Sin Seguimiento de Experimentos)

```bash
uv run python scripts/train_no_mlflow.py
```

Entrena un `RandomForestRegressor` y reporta el RMSE por log, sin dejar ningún
registro persistente del experimento.

#### b. MLflow Básico

Primero levanta el MLflow Tracking Server (en otra terminal, desde la raíz del
módulo):

```bash
mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns
```

Luego, en la terminal original:

```bash
uv run python scripts/train_with_basic_mlflow.py
```

Esto registra los parámetros y métricas del modelo en el Tracking Server.

#### c. MLflow Avanzado (Optimización de Hiperparámetros)

Con el Tracking Server del paso anterior corriendo:

```bash
uv run python scripts/train_with_full_mlflow.py
```

Ejecuta 10 trials de Optuna y registra cada uno como un run en MLflow.

### 4. Visualizando los Resultados en la Interfaz de MLflow

Con el Tracking Server corriendo, abre en tu navegador:

```
http://127.0.0.1:5000
```

## Notebooks

* **00_data_preparation.ipynb:** descarga y preprocesa el dataset, y genera un
  `metadata.json` con checksum de los datos (versión de datos).
* **01_first_steps_without_tracking.ipynb:** entrena un modelo sin ningún tracking,
  para dejar en evidencia el problema que resuelve MLflow.
* **02_experiment_tracking_intro.ipynb:** introduce MLflow — params, métricas, tags,
  artifacts y autologging. Incluye un ejercicio de equipo.
* **03_mlflow_advanced.ipynb:** optimización de hiperparámetros con Optuna (nested
  runs) y uso del Model Registry (versiones y aliases). Incluye un ejercicio de equipo.

## Escenarios de Arquitectura MLflow

* **scenario-1.ipynb:** sin Tracking Server, todo en archivos locales. Útil para
  trabajo individual (por ejemplo, una competencia de Kaggle).
* **scenario-2.ipynb:** Tracking Server local con backend SQLite. Útil para un equipo
  pequeño trabajando en la misma red. Incluye un ejercicio de equipo.
* **scenario-3.ipynb:** Tracking Server en AWS (EC2 + RDS Postgres + S3). Arquitectura
  de referencia para un equipo distribuido en un entorno tipo producción.

## Ejercicios de Equipo

Los notebooks 01, 02 y 03, y el escenario 2, incluyen ejercicios pensados para
resolverse en equipos de 2-3 personas (por ejemplo, en salas de breakout de Zoom).
Cada ejercicio indica el tiempo sugerido y qué debe compartir el equipo en la
plenaria al finalizar.
