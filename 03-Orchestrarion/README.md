# Modulo 03: Orquestacion de Pipelines ML

## Objetivo

Aprender a **automatizar y coordinar** las etapas de un pipeline de ML
(ingesta, preprocesamiento, entrenamiento, evaluacion) usando herramientas
de orquestacion. Al finalizar, tendras un pipeline reproducible y
monitoreable con Prefect.

## Que es la orquestacion en ML?

La orquestacion es la coordinacion automatica de tareas que componen
el ciclo de vida de un proyecto de ML. Su objetivo es que cada paso
se ejecute en el orden correcto, de manera reproducible y escalable.

```
Sin orquestacion:                    Con orquestacion:
  "Corro el script a mano"            Pipeline automatizado
  "Se me olvido preprocesar"           Dependencias explicitas
  "No se que version use"              Versionado automatico
  "Fallo y no me entere"               Reintentos + alertas
```

## Por que es importante?

| Problema | Como lo resuelve la orquestacion |
|----------|--------------------------------|
| Errores manuales | Automatizacion: el pipeline corre igual cada vez |
| "Funciona en mi maquina" | Reproducibilidad: mismos datos + mismos pasos = mismo resultado |
| Escalar a mas datos | Escalabilidad: el orquestador maneja recursos |
| Colaboracion en equipo | Cada tarea esta documentada y es independiente |

## Estructura del modulo

```
03-Orchestrarion/
├── README.md                              <-- Estas aqui
├── duration-prediction.ipynb              <-- Notebook interactivo (explorar el pipeline)
├── duration-prediction.py                 <-- Script standalone (version produccion)
├── models/
│   └── preprocessor.b                     <-- DictVectorizer serializado
└── Prefect-pipelines/
    ├── README.md                          <-- Guia detallada del pipeline Prefect
    ├── duration_prediction_prefect.py     <-- Pipeline orquestado con Prefect
    └── models/
        └── preprocessor_old.b
```

## Progresion pedagogica

El modulo sigue una progresion de **notebook a produccion**:

### Paso 1: Notebook interactivo (`duration-prediction.ipynb`)

Explora y entiende el pipeline de ML paso a paso:
- Descarga datos de taxis NYC (2021)
- Feature engineering: `PU_DO` = pickup + dropoff
- Encoding con `DictVectorizer`
- Entrenamiento XGBoost con MLflow tracking
- RMSE progresa de 11.44 a 6.61

### Paso 2: Script standalone (`duration-prediction.py`)

Refactoriza el notebook a un script parametrizado:

```bash
uv run python duration-prediction.py --year 2023 --month 1
```

Funciones bien definidas: `read_dataframe()`, `create_X()`, `train_model()`, `run()`.
Calcula automaticamente el mes siguiente para validacion.

### Paso 3: Pipeline con Prefect (`Prefect-pipelines/`)

Agrega orquestacion al script:
- Decoradores `@task` y `@flow`
- Reintentos automaticos (`retries=3`)
- Logging estructurado
- Artifacts (reportes y tablas en el dashboard de Prefect)
- Integracion con MLflow

Consulta `Prefect-pipelines/README.md` para instrucciones detalladas de ejecucion.

## Como ejecutar

### Opcion A: Script directo (sin orquestacion)

```bash
# Requiere MLflow server corriendo en localhost:5000
uv run mlflow server --backend-store-uri sqlite:///mlflow.db &
uv run python duration-prediction.py --year 2023 --month 1
```

### Opcion B: Pipeline con Prefect

```bash
# Terminal 1: Iniciar Prefect server
uv run prefect server start

# Terminal 2: Configurar y ejecutar
uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
cd Prefect-pipelines
uv run python duration_prediction_prefect.py --year 2023 --month 1
```

Ver resultados:
- Prefect dashboard: http://127.0.0.1:4200
- MLflow UI: `uv run mlflow ui --backend-store-uri sqlite:///mlflow.db`

## Herramientas de orquestacion

| Herramienta | Descripcion | Caso de uso |
|-------------|------------|-------------|
| **Prefect** | Orquestacion moderna, facil de usar | Este curso |
| **Airflow** | Estandar de la industria, flexible y robusto | Pipelines complejos |
| **Dagster** | Fuerte tipado y testing de pipelines | Data engineering |
| **Kubeflow** | Orquestacion sobre Kubernetes | ML a escala en la nube |
| **Metaflow** | Simplicidad para data scientists, integracion AWS | Netflix/AWS |

## Conceptos clave de Prefect

| Concepto | Definicion |
|----------|-----------|
| **Flow** | La funcion principal que define el pipeline completo |
| **Task** | Una unidad de trabajo individual dentro de un flow |
| **Run** | Una ejecucion especifica de un flow |
| **Artifact** | Datos generados por un flow (tablas, reportes, archivos) |
| **Deployment** | Configuracion para ejecutar un flow de forma programada |
| **Work Pool** | Infraestructura donde se ejecutan los flows |

## Conexion con otros modulos

```
Modulo 02 (Experiment Tracking)    Modulo 04 (Deployment)
        |                                   ^
        v                                   |
    Orquestacion (este modulo)
    - Automatiza entrenamiento
    - Registra en MLflow
    - Genera artifacts
    - Prepara para deployment
```
