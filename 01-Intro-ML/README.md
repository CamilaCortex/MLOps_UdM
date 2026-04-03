# Modulo 01: Introduccion a Machine Learning

## Objetivo

Construir un **pipeline de ML completo** de clasificacion utilizando datos sinteticos,
con enfasis en buenas practicas: prevencion de data leakage, pipelines reproducibles,
y evaluacion rigurosa del modelo.

## Contenido

### Notebook: `01_mlops_intro_notebook.ipynb`

El notebook recorre paso a paso un flujo de ML completo:

| Seccion | Que se aprende |
|---------|---------------|
| Data Leakage | Que es, por que ocurre, como prevenirlo con Pipelines |
| Generacion de datos | Crear datasets sinteticos realistas con nulos intencionales |
| EDA | Explorar tipos de datos, distribuciones, valores faltantes |
| Feature Engineering | Crear variables derivadas y bins categoricos |
| Train/Test Split | Dividir datos correctamente antes de preprocesar |
| Pipeline de Preprocesamiento | `ColumnTransformer` + `Pipeline` (numerico + categorico) |
| Entrenamiento | `LogisticRegression` dentro del pipeline |
| Evaluacion | Classification report, matriz de confusion, ROC-AUC |
| Analisis de umbral | Efecto de thresholds en precision/recall |

### Script: `generate_data.py`

Genera 10,000 usuarios sinteticos de e-commerce para un problema de targeting de promociones.

**Features generadas**:
- Perfil: `age_group`, `location`, `device_type`, `subscription_type`
- Transaccional: `total_purchases`, `avg_order_value`, `last_purchase_days`
- Engagement: `sessions_last_30_days`, `time_on_site_minutes`, `pages_per_session`
- Conversion: `cart_abandonment_rate`, `purchase_frequency`

**Nota sobre el target**: `dar_promocion` se asigna aleatoriamente. Esto es **intencional** —
el modelo no puede aprender patrones reales (ROC-AUC ~ 0.5), lo cual permite enfocarse
en el proceso y no en los resultados.

## Como ejecutar

```bash
# Generar el dataset (opcional, el notebook lo genera internamente)
uv run python generate_data.py

# Abrir el notebook
jupyter notebook 01_mlops_intro_notebook.ipynb
```

## Herramientas utilizadas

- **pandas** / **numpy**: Manipulacion de datos
- **matplotlib** / **seaborn**: Visualizacion
- **scikit-learn**: Pipeline, ColumnTransformer, StandardScaler, OneHotEncoder,
  SimpleImputer, LogisticRegression, classification_report, confusion_matrix, roc_auc_score

## Actividad para los estudiantes

Al final del notebook hay un ejercicio que pide:

1. Probar diferentes estrategias de imputacion para numericas
2. Crear nuevas features
3. Usar `BinaryEncoder` para categoricas
4. Usar `MinMaxScaler` para numericas
5. Usar `RandomForestClassifier`
6. Usar `GridSearchCV` para tuning de hiperparametros
7. Experimentar con el split de datos
8. Subir la solucion a su repositorio individual

## Conexion con el siguiente modulo

En este modulo entrenamos un modelo pero **no guardamos nada**: ni parametros,
ni metricas, ni el modelo en si. En el **Modulo 02 (Experiment Tracking)** aprenderemos
a resolver exactamente ese problema con MLflow.
