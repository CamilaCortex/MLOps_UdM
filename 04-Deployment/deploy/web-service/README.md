# NYC Taxi Duration Prediction API

API REST con FastAPI para predecir la duración de viajes de taxi en NYC, con interfaz web interactiva.

## Características

- **API REST** con FastAPI
- **Interfaz web moderna** para hacer predicciones
- **Documentación automática** (Swagger UI)
- **Validación de datos** con Pydantic
- **Modelo XGBoost** entrenado con MLflow
- **Dockerizado** y listo para producción

---

## Estructura del Proyecto

```
web-service/
├── app.py                  # API FastAPI principal
├── src/
│   ├── model_loader.py     # Carga del modelo
│   └── schemas.py          # Esquemas Pydantic
├── templates/
│   └── index.html          # Interfaz web
├── model/                  # Modelo MLflow (copiar antes de usar)
├── Dockerfile              # Imagen Docker
├── docker-compose.yml      # Orquestación Docker
├── copy_model.py           # Script para copiar modelo
└── README.md               # Esta guía
```

---

## Opción 1: Ejecución Local (Sin Docker)

### Paso 1: Copiar el Modelo

```bash
cd 04-Deployment/deploy/web-service
uv run python copy_model.py
```

### Paso 2: Instalar Dependencias

```bash
uv sync
```

### Paso 3: Ejecutar la API

```bash
uv run uvicorn app:app --host 127.0.0.1 --port 8000
```

### Paso 4: Abrir la Interfaz Web

```bash
open http://localhost:8000
```

O abre en tu navegador: **http://localhost:8000**

---

## Opción 2: Ejecución con Docker

### Paso 1: Copiar el Modelo

```bash
cd 04-Deployment/deploy/web-service
uv run python copy_model.py
```

### Paso 2: Construir la Imagen

```bash
docker build -t nyc-taxi-api .
```

### Paso 3: Ejecutar el Contenedor

**Opción A: Ver logs directamente**
```bash
docker run -p 8000:8000 --name nyc-taxi-api nyc-taxi-api
```

**Opción B: Ejecutar en background**
```bash
docker run -d -p 8000:8000 --name nyc-taxi-api nyc-taxi-api

# Ver logs
docker logs -f nyc-taxi-api
```

### Paso 4: Abrir la Interfaz Web

```bash
open http://localhost:8000
```

---

## Opción 3: Docker Compose (Más Fácil)

### Paso 1: Copiar el Modelo

```bash
uv run python copy_model.py
```

### Paso 2: Levantar con Docker Compose

```bash
docker-compose up --build
```

### Paso 3: Abrir la Interfaz Web

```bash
open http://localhost:8000
```

### Detener

```bash
docker-compose down
```

---

## Interfaz Web

La interfaz web incluye:

- **Campo de Zona de Recogida** (PULocationID: 1-265)
- **Campo de Zona de Destino** (DOLocationID: 1-265)
- **Campo de Distancia** (en millas)
- **Botón de Predicción**
- **Resultado con duración estimada** en minutos
- **Información del modelo** usado

### Ejemplo de Uso

1. Abre http://localhost:8000
2. Ingresa los datos del viaje (valores por defecto ya están cargados)
3. Click en "Predecir Duración"
4. Ve el resultado con la duración estimada

---

## Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Interfaz web interactiva |
| `/health` | GET | Health check |
| `/predict` | POST | Predicción individual |
| `/predict/batch` | POST | Predicción por lotes |
| `/docs` | GET | Documentación Swagger UI |
| `/redoc` | GET | Documentación ReDoc |

---

## Probar la API con cURL

### Health Check

```bash
curl http://localhost:8000/health
```

### Predicción Individual

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "PULocationID": 161,
    "DOLocationID": 236,
    "trip_distance": 5.2
  }'
```

**Respuesta esperada:**
```json
{
  "PULocationID": 161,
  "DOLocationID": 236,
  "trip_distance": 5.2,
  "predicted_duration_minutes": 8.86,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "2"
}
```

### Predicción por Lotes

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "trips": [
      {"PULocationID": 161, "DOLocationID": 236, "trip_distance": 5.2},
      {"PULocationID": 237, "DOLocationID": 140, "trip_distance": 3.8}
    ]
  }'
```

---

## Comandos Docker Útiles

### Ver Contenedores

```bash
docker ps                 # Activos
docker ps -a              # Todos
```

### Ver Logs

```bash
docker logs nyc-taxi-api           # Ver logs
docker logs -f nyc-taxi-api        # Seguir logs en tiempo real
docker logs --tail 50 nyc-taxi-api # Últimas 50 líneas
```

### Detener y Limpiar

```bash
docker stop nyc-taxi-api   # Detener
docker rm nyc-taxi-api     # Eliminar contenedor
docker rmi nyc-taxi-api    # Eliminar imagen
```

### Reconstruir Después de Cambios

```bash
docker rm -f nyc-taxi-api
docker rmi nyc-taxi-api
docker build -t nyc-taxi-api .
docker run -p 8000:8000 --name nyc-taxi-api nyc-taxi-api
```

---

## Postman Collection

Incluye una colección de Postman con todos los endpoints:

1. Importa `NYC_Taxi_API.postman_collection.json`
2. Importa `NYC_Taxi_API.postman_environment.json`
3. Selecciona el environment "NYC Taxi API - Local"
4. Prueba los endpoints

---

## Actualizar el Modelo

1. Entrena un nuevo modelo con MLflow
2. Copia el nuevo modelo:
   ```bash
   uv run python copy_model.py
   ```
3. Reconstruye la imagen Docker:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

---

## Ventajas de Docker

| Aspecto | Sin Docker | Con Docker |
|---------|------------|------------|
| **Instalación** | Instalar Python, dependencias, etc. | Solo Docker |
| **Portabilidad** | "Funciona en mi máquina" | Funciona en cualquier lugar |
| **Reproducibilidad** | Difícil | Garantizada |
| **Aislamiento** | Conflictos de versiones | Entorno aislado |
| **Despliegue** | Complejo | Simple |

---

## Despliegue a Producción

### AWS ECS / Fargate

```bash
# Tag de la imagen
docker tag nyc-taxi-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/nyc-taxi-api:latest

# Push a ECR
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/nyc-taxi-api:latest
```

### Google Cloud Run

```bash
gcloud run deploy nyc-taxi-api \
  --image nyc-taxi-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name nyc-taxi-api \
  --image nyc-taxi-api:latest \
  --dns-name-label nyc-taxi-api \
  --ports 8000
```

---

## Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## Troubleshooting

### Error: "No module named uvicorn"

Reconstruye la imagen Docker:
```bash
docker rmi nyc-taxi-api
docker build -t nyc-taxi-api .
```

### Error: "model/ directory not found"

Copia el modelo primero:
```bash
uv run python copy_model.py
```

### Puerto 8000 ya en uso

Cambia el puerto:
```bash
docker run -p 9000:8000 --name nyc-taxi-api nyc-taxi-api
# Abre: http://localhost:9000
```

---

**Listo para predecir duraciones de viajes de taxi.**
