# NYC Taxi Duration Prediction API (AWS EC2)

API REST con Flask + gunicorn para predecir la duración de viajes de taxi en NYC, empaquetada en Docker para desplegarse en una instancia EC2 de AWS y probarse desde Postman.

Esta es la variante pensada para AWS EC2. Si buscas la API con FastAPI, interfaz web e interfaz Swagger, esa es `../web-service/`.

---

## Estructura del Proyecto

```
web-service-aws/
├── predict.py              # API Flask (endpoints /health y /predict)
├── src/
│   └── model_loader.py     # Carga del modelo (MLflow + skops)
├── model/                  # Modelo MLflow (copiar antes de usar, ver Paso 1)
├── copy_model.py           # Script para copiar el modelo "champion" desde MLflow
├── Dockerfile              # Imagen Docker (gunicorn, puerto 9696)
├── test.py                 # Script simple para probar la API sin Postman
├── NYC_Taxi_API_AWS.postman_collection.json
├── NYC_Taxi_API_AWS.postman_environment.json
├── GUIA_AWS_EC2.md         # Guía paso a paso para desplegar en EC2
└── README.md               # Esta guía
```

---

## Paso 1: Copiar el Modelo

El modelo (XGBoost en formato `.ubj`) y el preprocessor (`DictVectorizer` guardado con `skops`) no están en este directorio ni en git -hay que copiarlos desde el registro de MLflow antes de poder construir la imagen o correr la API:

```bash
cd 04-Deployment/deploy/web-service-aws
uv run python copy_model.py
```

Esto crea `model/models_mlflow/` y `model/preprocessor/` con el modelo "champion" actual.

## Paso 2: Instalar Dependencias

```bash
uv sync
```

## Paso 3: Ejecutar la API en Local (sin Docker)

```bash
uv run python predict.py
```

Prueba con `curl`:

```bash
curl http://localhost:9696/health

curl -X POST http://localhost:9696/predict \
  -H "Content-Type: application/json" \
  -d '{"PULocationID": 161, "DOLocationID": 236, "trip_distance": 5.2}'
```

O corre `python test.py`, que hace las dos pruebas por ti.

## Paso 4: Construir la Imagen Docker (con el modelo ya adentro)

```bash
docker build -t taxi-prediction-aws .
```

> Importante: el modelo debe estar copiado (Paso 1) **antes** de este build - el `Dockerfile` hace `COPY model/ ./model/`, así que la imagen queda con el modelo y el preprocessor horneados adentro. Esto es intencional: la instancia EC2 no tiene acceso al registro de MLflow ni al directorio `03-Orchestration/Prefect-pipelines/models/` (está excluido de git), así que la imagen tiene que llevar el modelo consigo.

## Paso 5: Probar el Contenedor en Local

```bash
docker run -d -p 9696:9696 --name taxi-prediction-aws taxi-prediction-aws
docker logs -f taxi-prediction-aws
curl http://localhost:9696/health
```

## Paso 6: Desplegar en EC2

Ver la guía completa en [`GUIA_AWS_EC2.md`](./GUIA_AWS_EC2.md): crear una instancia EC2 gratuita, clonar este repositorio directamente en ella (el modelo ya viene versionado en git dentro de esta carpeta, así que no hace falta MLflow ni Docker Hub) y construir la imagen ahí mismo.

---

## Endpoints de la API

| Endpoint  | Método | Descripción                                  |
|-----------|--------|-----------------------------------------------|
| `/health` | GET    | Health check (confirma que el modelo cargó)  |
| `/predict`| POST   | Predicción individual                        |

### Ejemplo de respuesta de `/predict`

```json
{
  "duration": 8.86,
  "pickup_location": 161,
  "dropoff_location": 236,
  "trip_distance": 5.2,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "2"
}
```

---

## Postman

1. Importa `NYC_Taxi_API_AWS.postman_collection.json`
2. Importa `NYC_Taxi_API_AWS.postman_environment.json`
3. Selecciona el environment "NYC Taxi API - AWS EC2"
4. Edita la variable `base_url` con el DNS público de tu instancia EC2 (o déjalo en `http://localhost:9696` para probar en local)
5. Prueba los endpoints

---

## Troubleshooting

### `model/ directory not found` o `FileNotFoundError` al iniciar

Copia el modelo primero:
```bash
uv run python copy_model.py
```

### Error al cargar el modelo (versión incompatible de scikit-learn / xgboost / skops)

El preprocessor se guardó con skops y el modelo XGBoost en formato `.ubj`; ambos formatos son sensibles a la versión exacta de las librerías con las que se guardaron. Revisa qué versiones declaró MLflow al momento de guardarlo:

```bash
cat model/preprocessor/requirements.txt
cat model/models_mlflow/requirements.txt
```

Y actualiza las versiones en `pyproject.toml` para que coincidan exactamente (sobre todo `scikit-learn` y `skops`), luego:

```bash
uv sync
docker build -t taxi-prediction-aws .   # si usas Docker, reconstruye la imagen también
```

### Puerto 9696 ya en uso

```bash
docker run -d -p 9000:9696 --name taxi-prediction-aws taxi-prediction-aws
# la API queda accesible en http://localhost:9000
```

### La API responde 400 con "Faltan campos requeridos"

El body del POST a `/predict` debe traer `PULocationID`, `DOLocationID` y `trip_distance`. Revisa el header `Content-Type: application/json` y que el JSON esté bien formado.

### El SSH a la instancia EC2 se queda "pegado" (no conecta ni da error)

Casi siempre es la regla de SSH del grupo de seguridad, no la clave `.pem`. La causa más común: tu IP pública no es fija (redes de universidad, wifi compartido o VPN suelen rotarte entre varias IPs) y la regla quedó apuntando a una IP vieja. Ver la sección "El SSH se queda pegado" en [`GUIA_AWS_EC2.md`](./GUIA_AWS_EC2.md) para el diagnóstico completo y las dos formas de resolverlo.

---

**Listo para predecir duraciones de viajes de taxi desde AWS EC2.**
