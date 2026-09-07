
# Curso MLOps: Orquestación de Pipelines con Prefect

Introducción práctica a la orquestación de flujos de trabajo con Prefect,
desde los conceptos básicos (flows, tasks, deployments, schedules) hasta un
pipeline de Machine Learning completo que integra Prefect con MLflow y
Optuna para entrenar y registrar un modelo de predicción de duración de
viajes en taxi de NYC.

## Estructura del Proyecto

```
.
├── README.md
├── 00-intro-prefect/           # Conceptos básicos de Prefect, paso a paso
│   ├── prefect.yaml            # Config de deployment declarativo
│   ├── flows/                  # Progresión: flow simple -> serve -> deploy -> schedule
│   ├── workflows/              # Ejemplos puntuales: tasks, retries, blocks, variables, artifacts
│   └── infrastructure/
│       └── prefect-yaml-guide.md
└── Prefect-pipelines/          # Pipeline de ML completo con Prefect + MLflow + Optuna
    ├── pipeline.py              # Flow principal (orquesta todo el pipeline)
    ├── deploy.py                # Deployment del pipeline con schedule
    ├── README_MODEL_REGISTRY.md # Cómo se registra el modelo (aliases champion/candidate)
    └── src/
        ├── config/              # Constantes y setup de MLflow
        ├── data/                # Carga, validación y utilidades de datos
        ├── features/            # Ingeniería de features
        └── models/              # Optimización (Optuna), entrenamiento y Model Registry
```

## Comenzando

Este módulo usa el entorno de todo el repositorio (`MLOps_UdM`), gestionado con `uv`:

```bash
# Desde la raíz del repositorio (MLOps_UdM/)
uv sync
```

Adicionalmente necesitas un servidor de Prefect corriendo localmente (en otra terminal):

```bash
uv run prefect server start
```

Y, para la parte de `Prefect-pipelines`, un Tracking Server de MLflow (ver el README del módulo de Tracking para el comando exacto).

## 00-intro-prefect: Conceptos Básicos

Los archivos en `flows/` siguen una progresión pensada para leerse en orden:

1. **weather1-bare.py**: un `@flow` simple, sin servir ni desplegar. Solo se ejecuta una vez al correr el script.
2. **weather1-flow.py**: el mismo flow, ya con `log_prints=True` para que los `print()` aparezcan como logs en la UI de Prefect.
3. **weather1-serve.py**: usa `.serve()` para mantener el flow corriendo y disponible para ejecuciones manuales o programadas.
4. **weather1-serve-schedule.py** / **weather1-serve-params.py**: `.serve()` con cron schedule y con parámetros por defecto distintos.
5. **weather1-deploy.py**: usa `.deploy()` (pensado para Prefect Cloud/trabajo distribuido) en vez de `.serve()`.
6. **serve-two-flows.py** / **serve-two-flows-scheduled.py**: cómo servir varios flows distintos desde un mismo proceso, con `to_deployment()` y `serve()`.
7. **prefect.yaml**: la alternativa declarativa (YAML) a `.deploy()` en código. Antes de usarlo, exporta `PREFECT_PROJECT_DIR` con la ruta absoluta de esta carpeta (ver comentario en el archivo) — así el archivo no depende de la ruta personal de nadie.

En `workflows/` cada archivo ilustra un concepto puntual de Prefect:

- **my-first-task.py**: `@task` + `@flow`, con `retries` y un artifact de tabla.
- **create_secret.py** / **openai_with_secret.py**: cómo guardar y usar credenciales con `Secret` blocks (nunca hardcodeadas en el código).
- **get_variable.py**: cómo leer una `Variable` configurada desde la UI de Prefect.
- **retries.py**: mecanismo de reintentos automáticos ante fallos (simulado localmente, sin depender de un servicio externo).
- **runtime_context.py**: cómo acceder a metadata de la ejecución actual (nombre del run, parámetros, deployment) con `prefect.runtime`.
- **artifacts-ml.py** / **simple-artifacts.py**: cómo crear artifacts (markdown, tablas, links) para visualizar resultados de ML directamente en Prefect, sin herramientas externas. `simple-artifacts.py` es la versión resumida; `artifacts-ml.py` cubre más tipos de artifact.

## Prefect-pipelines: Pipeline de ML Completo

`pipeline.py` es el flow principal (`duration_prediction_flow`) que orquesta todo el proceso de principio a fin:

1. Carga y valida los datos de entrenamiento y validación (`src/data`)
2. Crea las features (`src/features`)
3. Optimiza hiperparámetros de XGBoost con Optuna (`src/models/optimization.py`)
4. Entrena el modelo final con los mejores hiperparámetros
5. Registra el modelo en el MLflow Model Registry (`src/models/model_registry.py`)

Para ejecutarlo:

```bash
cd Prefect-pipelines
uv run python pipeline.py --year 2025 --month 1
```

Para desplegarlo con un schedule (ejecuta el pipeline completo cada 2 minutos, solo para fines de aprendizaje):

```bash
uv run python deploy.py
```

### Registro del modelo: aliases, no stages

El Model Registry de MLflow tiene deprecado su sistema de "stages"
(`None -> Staging -> Production -> Archived`). Este pipeline usa en su
lugar **aliases**, siguiendo la misma práctica que ya viste en el módulo de
Tracking:

- Toda versión nueva del modelo se registra con el alias `candidate`.
- Esa versión solo se promueve además a `champion` si su RMSE es **mejor**
  que el del `champion` actual (o si todavía no existe un champion).

Así, correr el pipeline repetidamente (por ejemplo, en un deployment con
schedule cada 2 minutos) nunca reemplaza un buen modelo en producción por
uno peor. Los detalles completos están en
[`Prefect-pipelines/README_MODEL_REGISTRY.md`](Prefect-pipelines/README_MODEL_REGISTRY.md).

## Ejercicios de Equipo

Pensados para resolverse en equipos de 2-3 personas, por ejemplo en salas
de breakout de Zoom.

### Ejercicio 1: Retries y logging (15 min)

Tomen `00-intro-prefect/flows/weather1-flow.py` y modifíquenlo para que la
`@task` (creen una, extrayendo la llamada a la API a una función `@task`
separada) tenga `retries=3` y `retry_delay_seconds=[5, 10, 20]`. Corran el
flow y observen en los logs qué pasa si fuerzan un error (por ejemplo,
usando una URL inválida). Compartan en la plenaria: ¿en qué intento se
recuperó, o falló definitivamente?

### Ejercicio 2: Secrets y Variables (15 min)

Usando `create_secret.py` y `get_variable.py` como referencia, creen un
nuevo Secret block con un valor inventado (por ejemplo, una "API key" de
prueba) y una Variable con un umbral numérico. Escriban un pequeño flow que
lea ambos valores y los reporte por log. Discutan: ¿por qué es mejor usar
Secrets/Variables que hardcodear estos valores en el código?

### Ejercicio 3: Artifacts a la medida (20 min)

Tomando `simple-artifacts.py` como base, diseñen un nuevo artifact de tipo
tabla que resuma resultados de una "predicción por lotes" inventada (por
ejemplo: cantidad de registros procesados, tiempo total, cantidad de
errores). Créenlo dentro de un nuevo flow y revísenlo en la UI de Prefect,
en la pestaña Artifacts del run.

### Ejercicio 4: Trazar la lógica de champion/candidate (20 min)

Sin ejecutar código (o ejecutándolo si tienen MLflow disponible), lean
`Prefect-pipelines/src/models/model_registry.py` y respondan en equipo:

1. Si el pipeline corre por primera vez con RMSE = 7.2, ¿qué alias(es)
   recibe esa versión?
2. Si corre una segunda vez con RMSE = 7.5, ¿cambia el champion? ¿Qué
   alias(es) tiene la nueva versión?
3. Si corre una tercera vez con RMSE = 6.9, ¿qué cambia?
4. ¿Qué línea de código específica es la que decide si una versión se
   convierte en champion?

Compartan sus respuestas y verifíquenlas leyendo la función
`_get_champion_rmse` y la condición `promoted_to_champion`.
