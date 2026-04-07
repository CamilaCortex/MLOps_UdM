# Guía Completa - API de Predicción de Duración de Viajes

## 📋 Tabla de Contenidos
1. [Levantar la API](#levantar-la-api)
2. [Endpoints Disponibles](#endpoints-disponibles)
3. [Ejemplos con cURL](#ejemplos-con-curl)
4. [Ejemplos con Postman](#ejemplos-con-postman)
5. [Códigos de Respuesta](#códigos-de-respuesta)

---

## Levantar la API

### **Paso 1: Copiar el Modelo**

```bash
cd /MLOps_UdM/04-Deployment/deploy/web-service

# Copiar modelo desde batch-deploy
uv run python copy_model.py
```

**Salida esperada:**
```
INFO: Copiando modelo de batch-deploy a web-service...
INFO: Modelo: nyc-taxi-duration-predictor v1
INFO: RMSE: 7.3977
INFO: Modelo copiado exitosamente
```

### **Paso 2: Iniciar el Servidor**

```bash
# Iniciar API en modo desarrollo (con auto-reload)
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Salida esperada:**
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Iniciando API...
INFO: Modelo: nyc-taxi-duration-predictor v1
INFO: API lista para recibir requests
INFO: Application startup complete.
```

### **Paso 3: Verificar que Funciona**

Abre tu navegador en: **http://localhost:8000**

Deberías ver:
```json
{
  "message": "NYC Taxi Duration Prediction API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "predict": "/predict",
    "predict_batch": "/predict/batch",
    "docs": "/docs"
  }
}
```

---

## Endpoints Disponibles

### **1. GET /** - Información de la API
**Propósito:** Verificar que la API está corriendo y ver endpoints disponibles

**URL:** `http://localhost:8000/`

**Respuesta:**
```json
{
  "message": "NYC Taxi Duration Prediction API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "predict": "/predict",
    "predict_batch": "/predict/batch",
    "docs": "/docs"
  }
}
```

---

### **2. GET /health** - Health Check
**Propósito:** Verificar que el modelo está cargado y la API está saludable

**URL:** `http://localhost:8000/health`

**Respuesta:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "1",
  "model_rmse": 7.3977
}
```

**Códigos de respuesta:**
- `200 OK` - API saludable
- `503 Service Unavailable` - Modelo no cargado o error

---

### **3. POST /predict** - Predicción Individual
**Propósito:** Predecir la duración de UN viaje de taxi

**URL:** `http://localhost:8000/predict`

**Request Body:**
```json
{
  "PULocationID": 161,
  "DOLocationID": 236,
  "trip_distance": 5.2
}
```

**Parámetros:**
- `PULocationID` (int): Zona de recogida (1-265)
- `DOLocationID` (int): Zona de destino (1-265)
- `trip_distance` (float): Distancia en millas (0-100)

**Respuesta:**
```json
{
  "PULocationID": 161,
  "DOLocationID": 236,
  "trip_distance": 5.2,
  "predicted_duration_minutes": 18.45,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "1"
}
```

**Códigos de respuesta:**
- `200 OK` - Predicción exitosa
- `422 Unprocessable Entity` - Error de validación
- `500 Internal Server Error` - Error en predicción

---

### **4. POST /predict/batch** - Predicción Batch
**Propósito:** Predecir la duración de MÚLTIPLES viajes (hasta 1000)

**URL:** `http://localhost:8000/predict/batch`

**Request Body:**
```json
{
  "trips": [
    {
      "PULocationID": 161,
      "DOLocationID": 236,
      "trip_distance": 5.2
    },
    {
      "PULocationID": 237,
      "DOLocationID": 238,
      "trip_distance": 3.8
    },
    {
      "PULocationID": 239,
      "DOLocationID": 161,
      "trip_distance": 7.1
    }
  ]
}
```

**Respuesta:**
```json
{
  "predictions": [
    {
      "PULocationID": 161,
      "DOLocationID": 236,
      "trip_distance": 5.2,
      "predicted_duration_minutes": 18.45,
      "model_name": "nyc-taxi-duration-predictor",
      "model_version": "1"
    },
    {
      "PULocationID": 237,
      "DOLocationID": 238,
      "trip_distance": 3.8,
      "predicted_duration_minutes": 14.23,
      "model_name": "nyc-taxi-duration-predictor",
      "model_version": "1"
    },
    {
      "PULocationID": 239,
      "DOLocationID": 161,
      "trip_distance": 7.1,
      "predicted_duration_minutes": 22.67,
      "model_name": "nyc-taxi-duration-predictor",
      "model_version": "1"
    }
  ],
  "total": 3,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "1"
}
```

---

### **5. GET /docs** - Documentación Swagger UI
**Propósito:** Interfaz interactiva para probar la API

**URL:** `http://localhost:8000/docs`

Permite:
- Ver todos los endpoints
- Probar requests directamente desde el navegador
- Ver esquemas de datos
- Descargar especificación OpenAPI

---

### **6. GET /redoc** - Documentación ReDoc
**Propósito:** Documentación alternativa más limpia

**URL:** `http://localhost:8000/redoc`

---

## 🔧 Ejemplos con cURL

### **1. Health Check**

```bash
curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "1",
  "model_rmse": 7.3977
}
```

---

### **2. Predicción Individual**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "PULocationID": 161,
    "DOLocationID": 236,
    "trip_distance": 5.2
  }'
```

**Respuesta:**
```json
{
  "PULocationID": 161,
  "DOLocationID": 236,
  "trip_distance": 5.2,
  "predicted_duration_minutes": 18.45,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "1"
}
```

---

### **3. Predicción Batch (3 viajes)**

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "trips": [
      {
        "PULocationID": 161,
        "DOLocationID": 236,
        "trip_distance": 5.2
      },
      {
        "PULocationID": 237,
        "DOLocationID": 238,
        "trip_distance": 3.8
      },
      {
        "PULocationID": 239,
        "DOLocationID": 161,
        "trip_distance": 7.1
      }
    ]
  }'
```

---

### **4. Guardar Respuesta en Archivo**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "PULocationID": 161,
    "DOLocationID": 236,
    "trip_distance": 5.2
  }' \
  -o prediction_result.json
```

---

### **5. Ver Solo el Código de Estado**

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
```

**Respuesta:** `200`

---

## 📮 Ejemplos con Postman

### **Configuración Inicial**

1. **Abrir Postman**
2. **Crear nueva Collection**: "NYC Taxi API"
3. **Configurar Base URL**: `http://localhost:8000`

---

### **Request 1: Health Check**

**Método:** `GET`  
**URL:** `http://localhost:8000/health`  
**Headers:** Ninguno necesario

**Steps en Postman:**
1. Click en "New Request"
2. Nombre: "Health Check"
3. Método: GET
4. URL: `http://localhost:8000/health`
5. Click "Send"

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "1",
  "model_rmse": 7.3977
}
```

---

### **Request 2: Predicción Individual**

**Método:** `POST`  
**URL:** `http://localhost:8000/predict`  
**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "PULocationID": 161,
  "DOLocationID": 236,
  "trip_distance": 5.2
}
```

**Steps en Postman:**
1. Click en "New Request"
2. Nombre: "Predict Single Trip"
3. Método: POST
4. URL: `http://localhost:8000/predict`
5. Tab "Headers":
   - Key: `Content-Type`
   - Value: `application/json`
6. Tab "Body":
   - Seleccionar "raw"
   - Seleccionar "JSON" del dropdown
   - Pegar el JSON
7. Click "Send"

**Respuesta esperada:**
```json
{
  "PULocationID": 161,
  "DOLocationID": 236,
  "trip_distance": 5.2,
  "predicted_duration_minutes": 18.45,
  "model_name": "nyc-taxi-duration-predictor",
  "model_version": "1"
}
```

---

### **Request 3: Predicción Batch**

**Método:** `POST`  
**URL:** `http://localhost:8000/predict/batch`  
**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "trips": [
    {
      "PULocationID": 161,
      "DOLocationID": 236,
      "trip_distance": 5.2
    },
    {
      "PULocationID": 237,
      "DOLocationID": 238,
      "trip_distance": 3.8
    },
    {
      "PULocationID": 239,
      "DOLocationID": 161,
      "trip_distance": 7.1
    }
  ]
}
```

**Steps en Postman:**
1. Click en "New Request"
2. Nombre: "Predict Batch Trips"
3. Método: POST
4. URL: `http://localhost:8000/predict/batch`
5. Tab "Headers":
   - Key: `Content-Type`
   - Value: `application/json`
6. Tab "Body":
   - Seleccionar "raw"
   - Seleccionar "JSON"
   - Pegar el JSON
7. Click "Send"

---

### **Postman Collection (Importar)**

Puedes crear un archivo `NYC_Taxi_API.postman_collection.json`:

```json
{
  "info": {
    "name": "NYC Taxi Duration API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["health"]
        }
      }
    },
    {
      "name": "Predict Single Trip",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"PULocationID\": 161,\n  \"DOLocationID\": 236,\n  \"trip_distance\": 5.2\n}"
        },
        "url": {
          "raw": "http://localhost:8000/predict",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["predict"]
        }
      }
    },
    {
      "name": "Predict Batch Trips",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"trips\": [\n    {\n      \"PULocationID\": 161,\n      \"DOLocationID\": 236,\n      \"trip_distance\": 5.2\n    },\n    {\n      \"PULocationID\": 237,\n      \"DOLocationID\": 238,\n      \"trip_distance\": 3.8\n    }\n  ]\n}"
        },
        "url": {
          "raw": "http://localhost:8000/predict/batch",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["predict", "batch"]
        }
      }
    }
  ]
}
```

**Para importar en Postman:**
1. Click "Import" en Postman
2. Seleccionar el archivo JSON
3. Click "Import"

---

## Códigos de Respuesta HTTP

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| **200** | OK | Request exitoso |
| **422** | Unprocessable Entity | Error de validación (datos inválidos) |
| **500** | Internal Server Error | Error en el servidor/modelo |
| **503** | Service Unavailable | Modelo no cargado |

---

## Errores Comunes

### **Error 422: Validation Error**

**Causa:** Datos inválidos en el request

**Ejemplo:**
```json
{
  "detail": [
    {
      "loc": ["body", "trip_distance"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error"
    }
  ]
}
```

**Solución:** Verificar que:
- `PULocationID` y `DOLocationID` estén entre 1 y 265
- `trip_distance` sea mayor a 0 y menor o igual a 100

---

### **Error 503: Service Unavailable**

**Causa:** Modelo no cargado

**Solución:**
```bash
# Copiar modelo primero
uv run python copy_model.py

# Reiniciar API
uv run uvicorn app:app --reload
```

---

## Casos de Uso

### **1. Predicción en Tiempo Real**
```bash
# Un usuario solicita estimación de duración
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"PULocationID": 161, "DOLocationID": 236, "trip_distance": 5.2}'
```

### **2. Procesamiento Batch**
```bash
# Procesar múltiples viajes de un archivo
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d @trips.json
```

### **3. Monitoreo de Salud**
```bash
# Verificar cada 30 segundos
watch -n 30 curl -s http://localhost:8000/health
```

---

##  Resumen Rápido

```bash
# 1. Copiar modelo
uv run python copy_model.py

# 2. Iniciar API
uv run uvicorn app:app --reload

# 3. Verificar salud
curl http://localhost:8000/health

# 4. Hacer predicción
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"PULocationID": 161, "DOLocationID": 236, "trip_distance": 5.2}'

# 5. Ver documentación
open http://localhost:8000/docs
```

---

¡API lista para usar! 🎉
