# Modulo 01: Introduccion a Machine Learning

## Objetivo

Construir **pipelines de ML completos** utilizando datos sinteticos, con enfasis en
buenas practicas: prevencion de data leakage, pipelines reproducibles y evaluacion
rigurosa. Se cubren dos tipos de problemas: **clasificacion** y **regresion temporal**.

## Contenido

### Notebook 01: `01_mlops_intro_notebook.ipynb` — Clasificacion

Flujo completo de clasificacion binaria (targeting de promociones):

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
| Cross-Validation | Evaluacion robusta con KFold |

### Notebook 02: `02_regression_temporal_notebook.ipynb` — Regresion temporal

Flujo completo de regresion para predecir demanda diaria de un e-commerce:

| Seccion | Que se aprende |
|---------|---------------|
| Data Leakage temporal | Por que un split aleatorio miente en datos con tiempo |
| EDA temporal | Patrones semanales, mensuales, tendencia, eventos |
| Lag Features | Usar valores pasados como features (y por que no es leakage) |
| Split temporal | Corte por fecha: train=pasado, test=futuro |
| Pipeline + XGBoost | Preprocesamiento + modelo de gradient boosting |
| Metricas de regresion | MAE, RMSE, R², MAPE y como comunicarlas al negocio |
| TimeSeriesSplit | Cross-validation que respeta el orden temporal |
| Comparacion TimeSeriesSplit vs KFold | Demostrar que KFold da scores optimistas |
| Feature Importance | Que variables monitorear en produccion |
| Comparacion de modelos | XGBoost vs ExtraTrees vs Random Forest |

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

### Script: `generate_demand_data.py`

Genera 2 anios de demanda diaria de un e-commerce con patrones temporales reales.

**Features generadas**:
- Temporal: `day_of_week`, `month`, `is_weekend`, `days_since_start`
- Contexto: `temperature`, `is_special_event`, `has_campaign`, `campaign_spend`, `avg_catalog_price`
- Lags: `units_sold_lag_1`, `units_sold_lag_7`, `units_sold_rolling_7`, `units_sold_rolling_30`

**Nota sobre el target**: `units_sold` tiene patrones reales (estacionalidad, tendencia, lags),
por lo que el modelo si puede aprender y las metricas reflejan rendimiento real.

## Como ejecutar

```bash
# Notebook 01: Clasificacion
uv run python generate_data.py                     # generar datos (opcional)
jupyter notebook 01_mlops_intro_notebook.ipynb

# Notebook 02: Regresion temporal
uv run python generate_demand_data.py              # generar datos (opcional)
jupyter notebook 02_regression_temporal_notebook.ipynb
```

## Herramientas utilizadas

- **pandas** / **numpy**: Manipulacion de datos
- **matplotlib** / **seaborn**: Visualizacion (notebook 01)
- **plotly**: Visualizaciones interactivas (notebook 02)
- **scikit-learn**: Pipeline, ColumnTransformer, StandardScaler, OneHotEncoder,
  SimpleImputer, LogisticRegression, ExtraTreesRegressor, RandomForestRegressor,
  TimeSeriesSplit, cross_val_score, metricas de clasificacion y regresion
- **xgboost**: XGBRegressor para regresion con gradient boosting

## Actividades para los estudiantes

### Notebook 01

1. Probar diferentes estrategias de imputacion para numericas
2. Crear nuevas features
3. Usar `BinaryEncoder` para categoricas
4. Usar `MinMaxScaler` para numericas
5. Usar `RandomForestClassifier`
6. Usar `GridSearchCV` para tuning de hiperparametros
7. Experimentar con el split de datos

### Notebook 02

1. Cambiar la estrategia de imputacion (media vs mediana vs constante)
2. Agregar nuevas lag features (lag_14, lag_30, rolling_14)
3. Usar `GridSearchCV` con `TimeSeriesSplit` para buscar hiperparametros de XGBoost
4. Comparar metricas de `TimeSeriesSplit` vs `KFold` con 10 folds
5. Entrenar un modelo sin lag features y medir cuanto empeora
6. Investigar que pasa si se usa `train_test_split(shuffle=True)` en vez del corte temporal

Subir soluciones a repositorio individual.

## Conexion con el siguiente modulo

En este modulo entrenamos modelos pero **no guardamos nada**: ni parametros,
ni metricas, ni el modelo en si. En el **Modulo 02 (Experiment Tracking)** aprenderemos
a resolver exactamente ese problema con MLflow.
