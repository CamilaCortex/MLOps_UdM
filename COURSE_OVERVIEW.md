# Analisis Detallado del Curso MLOps

> **Curso original**: [CamilaCortex/MLOps_UdM](https://github.com/CamilaCortex/MLOps_UdM)
> **Instructores originales**: Maria Camila Durango ("Maca") y Mateo Cano Solis ("Mate") — ambos de MercadoLibre
> **Audiencia**: Estudiantes de Especializacion en Inteligencia Artificial

---

## Tabla de Contenidos

- [Vision General del Curso](#vision-general-del-curso)
- [Modulo 00 — Setup y Herramientas](#modulo-00--setup-y-herramientas)
- [Modulo 01 — Introduccion a ML](#modulo-01--introduccion-a-ml)
- [Modulo 02 — Experiment Tracking](#modulo-02--experiment-tracking)
- [Modulo 03 — Orquestacion](#modulo-03--orquestacion)
- [Modulo 04 — Deployment](#modulo-04--deployment)
- [Proyecto Final](#proyecto-final)
- [Material Complementario](#material-complementario)
- [Resumen de Herramientas](#resumen-de-herramientas)
- [Temas Faltantes y Oportunidades de Mejora](#temas-faltantes-y-oportunidades-de-mejora)

---

## Vision General del Curso

El curso sigue una progresion lineal que lleva al estudiante desde lo mas basico
(configurar un entorno) hasta desplegar un modelo en produccion:

```
00-Setup               Preparar el entorno de trabajo
    |
01-Intro-ML            Fundamentos: pipeline de ML completo (clasificacion)
    |
02-Experiment-Tracking Registrar, comparar y versionar experimentos con MLflow
    |
03-Orquestacion        Automatizar pipelines con Prefect
    |
04-Deployment          Servir modelos: web service, Docker, batch, cloud (AWS)
    |
Proyecto Final         Aplicar todo lo aprendido end-to-end
```

### Datasets utilizados

| Modulo | Dataset | Tipo de problema | Target |
|--------|---------|------------------|--------|
| 01 | Datos sinteticos de e-commerce (10K registros) | Clasificacion binaria | `dar_promocion` |
| 02-04 | NYC Green Taxi Trip Data (TLC, ~60K registros) | Regresion | `duration` (minutos) |

El dataset de taxis de NYC proporciona **continuidad** desde el modulo 02 hasta el 04:
el modelo entrenado en tracking es el mismo que se orquesta y despliega.

### Dependencias principales (pyproject.toml raiz)

```
scikit-learn==1.6.1, mlflow>=3.2.0, prefect>=3.4.12,
xgboost>=3.0.4, optuna>=4.4.0, pandas, numpy,
matplotlib, seaborn, gunicorn, pyarrow
```

---

## Modulo 00 — Setup y Herramientas

**Carpeta**: `00-Setup/`

### Archivos

| Archivo | Contenido |
|---------|-----------|
| `01-git-github.md` | Instalacion de Git, SSH keys, flujo diario (branch, commit, rebase, PR) |
| `02-python-envs.md` | Python 3.11+ via pyenv, entornos virtuales con `uv`, `venv` y Poetry |
| `03-dependency-management.md` | Comandos de `uv` y Poetry, lockfiles, checklist de reproducibilidad |
| `04-tooling.md` | VS Code extensions, Ruff, Black, pre-commit hooks |
| `05-data-and-secrets.md` | Manejo de `.env`, `python-dotenv`, GitHub Actions secrets |
| `06-github-actions.md` | Workflows CI completos para `uv` y Poetry (lint + test) |
| `07-os-notes.md` | Diferencias macOS vs Windows (shells, package managers, paths) |
| `Resumen.md` | Guia rapida condensada (enfocada en Windows) |
| `scripts/` | 4 scripts automatizados de setup (uv/Poetry x macOS/Windows) |
| `templates/` | `pyproject.toml` (uv y Poetry), `.gitignore` para Python |

### Que se ensena

Este modulo prepara al estudiante para que tenga un entorno profesional
funcional antes de tocar una linea de codigo de ML. Cubre:

1. **Git/GitHub**: Desde la instalacion hasta un flujo de trabajo con branches y PRs
2. **Python y entornos virtuales**: pyenv para manejar versiones, `uv` como gestor principal
3. **Dependencias**: El rol del lockfile, reproducibilidad, `uv add` vs `uv pip install` vs `uv sync`
4. **Calidad de codigo**: Linters (Ruff), formatters (Black), pre-commit hooks
5. **Secretos y datos**: Nunca commitear `.env`, uso de `python-dotenv`
6. **CI/CD**: GitHub Actions para lint y tests automaticos
7. **Notas de SO**: Troubleshooting comun de macOS vs Windows

### Ejemplos incluidos

- Scripts de setup automatizado que verifican prerequisitos, instalan herramientas y crean entornos
- Templates listos para copiar (`pyproject.toml`, `.gitignore`)
- Workflows YAML de GitHub Actions

### Que falta o se podria mejorar

- No hay un archivo `.pre-commit-config.yaml` de ejemplo a pesar de que se referencia en `04-tooling.md`
- No hay un `.env.example` template
- No hay archivos YAML de CI/CD en `templates/` para que los copien directamente
- El `Resumen.md` solo cubre Windows; falta uno para macOS
- No hay ejercicio practico definido para este modulo
- No se menciona Git LFS (aunque el repo lo usa para PNGs)

---

## Modulo 01 — Introduccion a ML

**Carpeta**: `01-Intro-ML/`

### Archivos

| Archivo | Contenido |
|---------|-----------|
| `01_mlops_intro_notebook.ipynb` | Notebook principal del modulo (~todo el contenido) |
| `generate_data.py` | Clase `UserGenerator` que crea datos sinteticos de e-commerce |

### Que se ensena

El notebook lleva al estudiante por un pipeline de ML completo de clasificacion:

1. **Data Leakage** — Que es, por que importa, como los Pipelines de scikit-learn lo previenen
   (ejemplo: calcular medianas en train+test vs solo train)

2. **Generacion de datos sinteticos** — La clase `UserGenerator` crea 10,000 usuarios de e-commerce con:
   - Datos demograficos: `age_group`, `location` (ciudades argentinas), `device_type`, `subscription_type`
   - Comportamiento transaccional: `total_purchases`, `avg_order_value`, `last_purchase_days`
   - Engagement: `sessions`, `time_on_site`, `pages_per_session`
   - Conversion: `cart_abandonment_rate`, `purchase_frequency`
   - Nulos inyectados intencionalmente (5-15% por columna) para simular datos reales

3. **EDA** — Tipos de datos (5 categoricas, 6 float, 4 int), porcentaje de nulos, histograma de `avg_order_value`

4. **Feature Engineering** — Variables derivadas:
   - `total_purchases_per_day`
   - `days_between_first_and_last_purchase`
   - `bucket_avg_order_value` (binned: low/medium/high)

5. **Train/Test Split** — `train_test_split(test_size=0.2, random_state=42)`

6. **Pipeline de Preprocesamiento**:
   - Numerico: `SimpleImputer(median)` + `StandardScaler`
   - Categorico: `SimpleImputer(constant="Unknown")` + `OneHotEncoder(drop="first")`
   - `ColumnTransformer` + `Pipeline` con `LogisticRegression`
   - 27 features finales (9 numericas + 18 one-hot)

7. **Metricas de clasificacion**:
   - `classification_report` (precision, recall, f1)
   - Matriz de confusion con heatmap
   - ROC-AUC Score (~0.517 — basicamente aleatorio, **intencional**)

8. **Analisis de umbral** — Thresholds de 0.3, 0.5 y 0.7 con explicacion del trade-off precision/recall
   y sus implicaciones de negocio (costo de falsos positivos vs falsos negativos en promociones)

### Ejercicio para los estudiantes

El notebook termina con una actividad explicita que pide:
1. Probar diferentes estrategias de imputacion
2. Crear nuevas features
3. Usar `BinaryEncoder` para categoricas
4. Usar `MinMaxScaler` para numericas
5. Usar `RandomForestClassifier`
6. Usar `GridSearchCV` para tuning
7. Experimentar con el split de datos
8. Subir la solucion al repositorio individual

### Que falta o se podria mejorar

- **No hay README** para este modulo (es el unico sin uno)
- No hay ejemplo de regresion (solo clasificacion); los modulos 02-04 usan regresion con otro dataset
- El modelo da ROC-AUC ~0.517 (aleatorio) porque el target es random. Pedagogicamente intencional,
  pero el estudiante nunca ve un "buen modelo" en este modulo
- No se demuestra cross-validation
- No se guarda el modelo (sin persistencia)
- No hay conexion con MLflow (eso viene en el modulo 02)
- El script `generate_data.py` guarda a CSV pero el notebook no lo referencia

---

## Modulo 02 — Experiment Tracking

**Carpeta**: `02-Experiment-Tracking/`

### Archivos

| Subcarpeta | Archivo | Contenido |
|------------|---------|-----------|
| `notebooks/` | `00_data_preparation.ipynb` | Descarga y preprocesa datos de taxis NYC |
| | `01_first_steps_without_tracking.ipynb` | Entrena modelo sin tracking (motiva el "por que") |
| | `02_experiment_tracking_intro.ipynb` | Introduccion a MLflow: logging manual y autolog |
| | `03_mlflow_advanced.ipynb` | Optuna HPO + Model Registry |
| `scripts/` | `preprocess_data.py` | Descarga, preprocesa y serializa datos |
| | `train_no_mlflow.py` | Entrenamiento baseline sin tracking (CLI con click) |
| | `train_with_basic_mlflow.py` | Entrenamiento + `log_param`/`log_metric` basico |
| | `train_with_full_mlflow.py` | Optuna HPO + logging por trial |
| `scenarios/` | `scenario-1.ipynb` | Kaggle-style: file store local, sin servidor |
| | `scenario-2.ipynb` | Equipo pequeno: MLflow server local (SQLite + artifacts) |
| | `scenario-3.ipynb` | Produccion: EC2 + RDS PostgreSQL + S3 |
| | `README.md` | Indice del modulo |

### Que se ensena

Este es el modulo mas robusto del curso. Progresion:

**Notebook 00 — Preparacion de datos**:
- Descarga datos de taxis verdes de NYC (enero + febrero 2023, formato parquet)
- Calcula feature `duration` (dropoff - pickup en minutos)
- Filtra viajes entre 1 y 60 minutos
- Genera `metadata.json` con checksums SHA256 para versionado de datos

**Notebook 01 — Sin tracking (motivacion)**:
- Carga datos procesados, EDA (distribucion de duracion, nulos)
- Define features: `PULocationID`, `DOLocationID` (categoricas) + `trip_distance` (numerica)
- Usa `DictVectorizer` + `ColumnTransformer` + `SimpleImputer` + `StandardScaler`
- Entrena `RandomForestRegressor(n_estimators=100, max_depth=10)`
- RMSE: 5.14 en validacion
- Termina con preguntas provocadoras: donde guardar hiperparametros? metricas? modelos?

**Notebook 02 — Intro a MLflow**:
- Panorama de herramientas: MLflow, W&B, Comet, TensorBoard
- Setup: `set_tracking_uri`, `set_experiment`, `start_run`
- Logging manual: `log_param`, `log_metric`, `set_tag`
- Artifacts: CSV de predicciones, plot de feature importance, histograma de residuales
- Comparacion RandomForest vs XGBoost (XGBoost gana: RMSE 4.98 vs 5.14)
- `mlflow.autolog()` combinado con logging personalizado
- Consulta programatica con `mlflow.search_runs()`

**Notebook 03 — MLflow Avanzado**:
- Estructura interna de `mlruns/` y artifacts
- **Optuna HPO con runs anidados**:
  - Parent run = estudio Optuna
  - Child runs = trials individuales (10 trials)
  - Hiperparametros: `n_estimators` (50-200), `max_depth` (3-15), `min_samples_split` (2-10), `min_samples_leaf` (1-4)
  - Mejor RMSE: 5.0234
- **Model Registry**:
  - Pipeline de produccion (preprocessor + model)
  - `mlflow.sklearn.log_model()` con `registered_model_name`
  - Model signature con `infer_signature`
  - Stages: None -> Staging -> Production -> Archived
  - Aliases: `champion`, `candidate`
  - Carga por version, por alias y por stage

**Escenarios de deployment de MLflow**:

| Escenario | Arquitectura | Cuando usarlo |
|-----------|-------------|---------------|
| 1 - Local file store | `file://mlruns`, sin servidor | Trabajo individual, Kaggle |
| 2 - Server local | SQLite backend + artifacts locales | Equipo pequeno, Model Registry habilitado |
| 3 - Produccion AWS | EC2 (server) + RDS PostgreSQL + S3 | Equipos grandes, produccion real |

**Scripts** (version CLI de los notebooks):
- Progresion: sin MLflow -> MLflow basico -> MLflow completo con Optuna
- Usan `click` para argumentos de linea de comandos

### Ejemplos incluidos

- 4 notebooks progresivos con outputs reales
- 3 scripts CLI con progresion de complejidad
- 3 escenarios de arquitectura (con diagramas)
- Visualizaciones de Optuna

### Que falta o se podria mejorar

- El README referencia `02_mlflow_basics.ipynb` que no existe (se llama `02_experiment_tracking_intro.ipynb`)
- No hay ejercicio/tarea explicito para los estudiantes
- El escenario 3 (AWS) es conceptual — las celdas no tienen outputs
- `train_with_full_mlflow.py` llama a `run_optimization()` dos veces (parece copy-paste)
- `click` no esta en las dependencias del `pyproject.toml` raiz
- No se introduce monitoreo ni data drift

---

## Modulo 03 — Orquestacion

**Carpeta**: `03-Orchestrarion/` *(nota: typo en el nombre de la carpeta)*

### Archivos

| Archivo | Contenido |
|---------|-----------|
| `README.md` | Introduccion conceptual a orquestacion de ML |
| `duration-prediction.ipynb` | Notebook interactivo: pipeline con MLflow + XGBoost |
| `duration-prediction.py` | Script standalone parametrizado (argparse) |
| `models/preprocessor.b` | Preprocessor serializado (pickle) |
| `Prefect-pipelines/README.md` | Guia completa del pipeline con Prefect |
| `Prefect-pipelines/duration_prediction_prefect.py` | Pipeline orquestado con `@task` y `@flow` |
| `Prefect-pipelines/models/` | Preprocessor anterior |
| `mlartifacts/` | Artifacts de MLflow |

### Que se ensena

**README conceptual**:
- Que es orquestacion en ML y por que importa (automatizacion, reproducibilidad, escalabilidad)
- Aspectos clave: pasos del pipeline, manejo de dependencias, versionado, error handling
- Tabla comparativa de herramientas: Airflow, Kubeflow, Prefect, Dagster, Metaflow

**Notebook interactivo** (`duration-prediction.ipynb`):
- Setup de kernel Jupyter para entornos `uv`
- Diferencia entre `mlflow.db` y `mlruns/` (metadata vs artifacts)
- Datos: NYC Green Taxi 2021-01 y 2021-02
- Feature engineering: `PU_DO` = combinacion pickup + dropoff
- `DictVectorizer` para encoding categorico
- Entrenamiento XGBoost:
  - `learning_rate=0.096`, `max_depth=30`, 30 boost rounds, early stopping a 50
  - RMSE progresa de 11.44 a 6.61
- Logging a MLflow: params, metricas, preprocessor como artifact, modelo XGBoost

**Script standalone** (`duration-prediction.py`):
- Mismo pipeline del notebook pero parametrizado con `argparse` (`--year`, `--month`)
- Calcula automaticamente el mes siguiente para datos de validacion
- Guarda `run_id.txt` para uso downstream

**Pipeline con Prefect** (`Prefect-pipelines/duration_prediction_prefect.py`):
- Decoradores `@task` y `@flow`
- Tres tasks: `read_dataframe` (con `retries=3`), `create_features`, `train_model`
- Type hints y docstrings en cada task
- Logging con `get_run_logger()`
- Artifacts de Prefect: `create_table_artifact`, `create_markdown_artifact`
- Integracion con MLflow (fallback a SQLite local si el server no esta disponible)
- Error handling robusto

### Progresion pedagogica

```
README (conceptos) -> Notebook (entender el pipeline) -> Script (refactorizar a produccion) -> Prefect (agregar orquestacion)
```

### Que falta o se podria mejorar

- **Typo en nombre de carpeta**: `03-Orchestrarion` en vez de `03-Orchestration`
- No hay ejercicio/tarea para los estudiantes
- El notebook usa datos de 2021 pero el script de Prefect usa 2023 (inconsistencia)
- `duration-prediction.py` usa `objective: 'reg:linear'` (deprecado); la version Prefect usa correctamente `'reg:squarederror'`
- No se demuestra scheduling/deployment de Prefect (se describe en README pero no hay config real)
- Los comentarios `TODO add docstrings` siguen en el codigo
- No hay comparacion practica con otras herramientas de orquestacion mas alla de la tabla

---

## Modulo 04 — Deployment

**Carpeta**: `04-Deployment/`

### Archivos

| Subcarpeta | Archivos clave | Contenido |
|------------|---------------|-----------|
| `deploy/web-service/` | `predict.py`, `test.py`, `README.md`, `README_CONCEPTOS.md` | Flask API para prediccion en tiempo real |
| `deploy/web-service-docker/` | `predict.py`, `test.py`, `Dockerfile`, 3 guias `.md` | Misma API containerizada con Docker |
| `deploy/batch-deploy/` | `src/`, `scripts/`, `config/`, `README.md` | Sistema batch con Prefect |
| `deploy/models/` | `lin_reg.bin` | Modelo de regresion lineal pre-entrenado |
| | `README.md` | Documento conceptual extenso (~1100 lineas) |

### Que se ensena

**README principal** — Documento conceptual muy completo que cubre tres estrategias de deployment:

| Estrategia | Descripcion | Ejemplo de uso |
|------------|-------------|----------------|
| **Batch/Offline** | Predicciones en lotes programados | Estimacion de duracion de flota, tarifas |
| **Web Service (Online)** | API REST para predicciones en tiempo real | Prediccion bajo demanda |
| **Streaming (Online)** | Procesamiento de eventos en tiempo real | Deteccion de fraude, pricing dinamico |

Incluye diagramas de arquitectura (mermaid), diagramas de secuencia, ejemplos de codigo
completos (FastAPI, Airflow DAG, Kafka consumers), patrones hibridos (Lambda, Kappa),
y una guia de decision para elegir estrategia.

---

**Web Service con Flask** (`deploy/web-service/`):

```python
# predict.py - Endpoints principales
POST /predict  -> Recibe PULocationID, DOLocationID, trip_distance -> Retorna duration
GET  /health   -> Health check
```

- Carga modelo pre-entrenado (`lin_reg.bin`: LinearRegression + DictVectorizer en pickle)
- Validacion de input, logging, error handling
- `test.py`: Cliente de testing con health check, prediccion basica, edge cases
- `README.md` (660 lineas): Guia para el estudiante con prerequisitos, setup con `uv`,
  tres metodos de deployment (Flask dev, Flask CLI, Gunicorn), testing con curl
- `README_CONCEPTOS.md`: Explicacion beginner-friendly de API, web service, endpoint, HTTP

---

**Web Service con Docker** (`deploy/web-service-docker/`):

```dockerfile
FROM python:3.11.9-slim
# Instala uv, copia deps, instala con uv pip, ejecuta con gunicorn
```

- Version simplificada del `predict.py`
- Tres guias detalladas:

| Guia | Contenido |
|------|-----------|
| `GUIA_DOCKER.md` | Conceptos Docker (imagenes, contenedores, Dockerfile, registry, volumes), comandos esenciales, ejemplos practicos (Nginx, PostgreSQL, Docker Compose), buenas practicas |
| `GUIA_INSTALACION.md` | Paso a paso: Python 3.11.9 (pyenv), uv, Docker, correr local y con Docker |
| `GUIA_AWS_EC2.md` | Deploy en AWS EC2: SSH, instalar Docker en Amazon Linux, build/run, security groups (puerto 9696), testing con Postman |

---

**Batch Deploy con Prefect** (`deploy/batch-deploy/`):

- `config/settings.py`: Paths, `NUM_TRIPS=1000`, schedule batch cada 2 horas
- `src/data_generator.py`: Genera datos sinteticos de taxis (locations aleatorias, trip_distance 0.5-10km)
- `src/batch_predictor.py`: Carga modelo, prepara features, predicciones batch, guarda parquet con timestamp
- `src/prefect_flows.py`: Flow de Prefect que encadena generacion + prediccion
- `scripts/deploy_prefect.py`: Deployments de Prefect (scheduled, cleanup, manual)
- `scripts/setup_batch_system.sh`: Script de setup completo del sistema
- `test_simple_flow.py`: Test del pipeline sin Prefect

### Progresion pedagogica

```
README conceptual (3 estrategias)
    |
Web Service con Flask (desarrollo local)
    |
Docker (containerizar el servicio)
    |
AWS EC2 (desplegar en la nube)
    |
Batch con Prefect (predicciones programadas)
```

### Que falta o se podria mejorar

- **FastAPI solo es conceptual**: El README tiene ~300 lineas de ejemplo FastAPI, pero la implementacion real usa Flask
- **Streaming solo es conceptual**: Kafka/Flink solo en el README, nada ejecutable
- **Codigo roto**: `deploy_prefect.py` referencia funciones que no existen en `prefect_flows.py`
  (`taxi_batch_prediction_flow` y `taxi_batch_cleanup_flow` vs el real `batch_completo_flow`)
- **Settings inconsistentes**: `deploy_prefect.py` usa `BATCH_SCHEDULE_CRON` y `CLEANUP_SCHEDULE_CRON`
  pero `settings.py` solo tiene `BATCH_SCHEDULE`
- No hay CI/CD implementado
- No hay monitoreo del modelo implementado
- No hay Kubernetes deployment files (solo mencionado en README)
- No hay ejercicio/tarea para estudiantes

---

## Proyecto Final

**Carpeta**: `Project/`

### Estructura

Un unico archivo `Readme.md` con las instrucciones del proyecto final.

### Que se pide

Un proyecto de ML end-to-end en **6 fases**:

| Fase | Entregable | Nice-to-have |
|------|-----------|--------------|
| 1. Planificacion y Setup | Repo Git, entorno virtual, EDA, baseline | Timeline con responsables |
| 2. Experiment Tracking | MLflow configurado, experimentos, Model Registry | — |
| 3. Pipeline de Entrenamiento | Prefect flows, ETL, feature engineering | Retraining automatico |
| 4. Deployment | Dockerfile, API REST (FastAPI), validacion | Cloud deployment, CI/CD |
| 5. Monitoreo | Proponer ideas de monitoreo | — |
| 6. Testing y Best Practices | Unit tests, linter, formatter, README | Pre-commit hooks |

### Evaluacion

- **Peer reviewing**: Cada estudiante debe evaluar 3 proyectos de companeros
- No hay rubrica de evaluacion detallada en el documento

### Recursos proporcionados

- Links a 8 fuentes de datasets (Kaggle, UCI, Google Research, AWS, etc.)
- Tecnologias recomendadas por categoria (cloud, tracking, orchestration, monitoring, CI/CD)
- Estructura de repositorio recomendada
- 7 consejos para el exito

### Que falta o se podria mejorar

- **No hay rubrica de evaluacion** (se menciona peer review pero no hay criterios de scoring)
- No hay timeline ni deadlines sugeridos
- No hay proyecto ejemplo ni starter template
- La fase de monitoreo es muy superficial ("proponer ideas" solamente)
- No se mencionan herramientas especificas de monitoreo de modelos (Evidently, Great Expectations)

---

## Material Complementario

### clase-entornos-virtuales

**Carpeta**: `clase-entornos-virtuales/`

Un README standalone de ~438 lineas, dedicado exclusivamente a `uv`:

1. Que es `uv` (Rust-based, 10-100x mas rapido que pip, PubGrub resolver)
2. Instalacion (pip, installer oficial, Homebrew)
3. Manejo de versiones de Python (`uv python install/list/pin`)
4. Inicializacion de proyectos (`uv init`, estructura generada)
5. `pyproject.toml` vs `uv.lock` (proposito de cada uno)
6. **Tres comandos de instalacion**: `uv add` (permanente) vs `uv pip install` (temporal) vs `uv sync` (reproducir)
7. `uv run` (ejecutar sin activar venv, util para cron/Airflow)
8. Manejo avanzado: `uv remove`, `uv update`, inline script dependencies (PEP 723)
9. Grupos de dependencias (`--group dev`, `--group docs`)
10. Herramientas globales (`uv tool install`, como pipx)
11. CI/CD con GitHub Actions (`astral-sh/setup-uv@v3`)
12. Tabla de referencia rapida de comandos

**Que falta**: No hay ejercicios, no hay comparacion con conda (comun en ciencia de datos).

---

## Resumen de Herramientas

### Implementadas (con codigo funcional)

| Categoria | Herramientas |
|-----------|-------------|
| Package Management | `uv` (principal), Poetry (alternativa), pip, pyenv |
| Version Control | Git, GitHub, Git LFS |
| ML/DS Core | scikit-learn, pandas, numpy, matplotlib, seaborn |
| Modelos | LogisticRegression, RandomForest, XGBoost |
| Experiment Tracking | MLflow (tracking, autolog, model registry) |
| Hyperparameter Tuning | Optuna |
| Orquestacion | Prefect 3.x |
| Web Framework | Flask |
| Production Server | Gunicorn |
| Containerizacion | Docker |
| Cloud | AWS (EC2, RDS, S3) |
| Code Quality | Ruff, Black, pre-commit |
| Data Formats | Parquet (pyarrow), pickle |

### Solo conceptuales (mencionadas en READMEs pero sin implementacion)

| Herramienta | Donde se menciona |
|-------------|-------------------|
| FastAPI | README de Deployment |
| Kafka / Flink | README de Deployment (streaming) |
| Kubernetes | README de Deployment |
| Airflow | README de Deployment y Orquestacion |
| Prometheus / Grafana | README de Deployment |
| Redis | README de Deployment |
| Evidently AI | No mencionada (faltante) |

---

## Temas Faltantes y Oportunidades de Mejora

### Gaps importantes

| Tema | Estado actual | Impacto |
|------|--------------|---------|
| **Monitoreo de modelos** | El README promete "Monitoreo" como objetivo pero no hay modulo dedicado | Alto — es un pilar de MLOps |
| **Data validation** | No se cubre | Medio — Great Expectations, Pandera, Pydantic |
| **Testing de modelos** | No hay tests de comportamiento, invarianza, etc. | Medio |
| **Feature store** | No se menciona | Bajo — avanzado para especializacion |
| **Streaming** | Solo conceptual en README | Bajo — puede ser avanzado |

### Inconsistencias y bugs conocidos

| Issue | Ubicacion | Severidad |
|-------|-----------|-----------|
| Typo en carpeta: `03-Orchestrarion` | Raiz del repo | Baja (cosmetico) |
| `deploy_prefect.py` referencia funciones inexistentes | `04-Deployment/deploy/batch-deploy/` | Alta (codigo roto) |
| README referencia notebook con nombre incorrecto | `02-Experiment-Tracking/README.md` | Baja |
| Script llama `run_optimization()` dos veces | `02-Experiment-Tracking/scripts/train_with_full_mlflow.py` | Media |
| `click` no esta en dependencias del pyproject.toml raiz | `02-Experiment-Tracking/scripts/` | Media |
| `reg:linear` deprecado | `03-Orchestrarion/duration-prediction.py` | Baja (warning) |
| Paths de instructores hardcodeados en outputs de notebooks | Varios notebooks | Baja |

### Oportunidades de mejora (sin desviarse del curso)

1. **Agregar README al modulo 01** — Es el unico sin uno
2. **Agregar ejercicios/tareas** a los modulos 02, 03, 04 — Solo el modulo 01 tiene actividad definida
3. **Crear un modulo ligero de monitoreo** — Al menos con Evidently para data drift
4. **Agregar rubrica de evaluacion** al proyecto final
5. **Unificar dataset en notebooks** — El modulo 03 usa datos 2021 vs 2023 en otros lados
6. **Corregir codigo roto** en batch deploy (funciones referenciadas que no existen)
7. **Agregar un `.pre-commit-config.yaml`** funcional (se ensena pero no se provee)
