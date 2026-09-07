# Módulo 01 — Introducción a ML y Pipelines de scikit-learn

Este módulo es el punto de partida del curso: antes de hablar de tracking (MLflow) u orquestación (Prefect), practicamos el flujo completo de un problema de clasificación binaria con `scikit-learn`, con especial énfasis en el objeto `Pipeline` y en evitar *data leakage*.

## Contenido

- **`01_mlops_intro_notebook.ipynb`** — el notebook principal del módulo. Recorre: generación de datos sintéticos, EDA mínimo, feature engineering, split train/test, `Pipeline` + `ColumnTransformer` de preprocesamiento, y evaluación (métricas, matriz de confusión, umbral de decisión).
- **`generate_data.py`** — genera el dataset sintético `usuarios_promociones.csv` (usuarios y su comportamiento transaccional, con valores faltantes simulados). El notebook lo importa directamente; no hace falta ejecutarlo por separado.
- **`clase-entornos-virtuales/README.md`** — guía de gestión de dependencias con `uv` (instalación, versiones de Python, `pyproject.toml`/`uv.lock`, integración con CI/CD).

## Por qué el dataset es sintético y aleatorio

La variable objetivo (`dar_promocion`) se genera al azar, sin relación real con ninguna feature. Esto es intencional: el objetivo del módulo no es lograr un buen score, sino practicar el flujo completo de un pipeline de ML de forma reproducible. Por eso el ROC-AUC del notebook da cerca de 0.5 — es el resultado esperado, no un error.

## Un detalle importante para tener en cuenta: valores centinela

`generate_data.py` usa `999` en `last_purchase_days` para marcar "todavía no ha comprado". Ese `999` no es una cantidad real de días: es una señal. El notebook incluye una nota explícita sobre esto en la sección de feature engineering, porque restar directamente sobre ese campo sin excluir el caso genera outliers artificiales (se verificó: hasta -988 en los datos de prueba).

## Ejercicios de equipo (salas de Zoom)

El notebook incluye, al final, cuatro ejercicios pensados para trabajarse en equipos de 2-3 personas durante la clase:

1. **Otra estrategia de imputación** (15 min) — cambiar `median` por `mean` y comparar.
2. **Una feature nueva, de principio a fin** (20 min) — crear una feature derivada y conectarla al `Pipeline`.
3. **Cambiar el umbral con criterio de negocio** (15 min) — justificar un umbral distinto a 0.5.
4. **Cambiar de modelo** (20 min) — reemplazar `LogisticRegression` por `RandomForestClassifier`.

Cada ejercicio termina con un entregable corto para compartir en la plenaria.

## Cómo correr el notebook

```bash
# Desde la raíz del repositorio
uv sync
uv run jupyter notebook 01-Intro-ML/01_mlops_intro_notebook.ipynb
```

El notebook genera `usuarios_promociones.csv` en esta misma carpeta la primera vez que se ejecuta (ya está excluido de git, ver `.gitignore`).
