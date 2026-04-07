# 🐳 Docker Deployment - NYC Taxi API

Deployment con Docker para la API de predicción de duración de viajes.

---

## 📋 Prerequisitos

- **Docker** instalado
- **Docker Compose** instalado (incluido con Docker Desktop)
- **Modelo copiado** en carpeta `model/`

---

## 🚀 Pasos para Desplegar

### **1. Copiar el Modelo**

Antes de construir la imagen, asegúrate de tener el modelo:

```bash
cd /Users/mdurango/Downloads/proyectos/MLOps_UdM/04-Deployment/deploy/web-service

uv run python copy_model.py
```

---

### **2. Construir la Imagen Docker**

```bash
docker build -t nyc-taxi-api .
```

**Salida esperada:**
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition
 => => transferring dockerfile: 456B
 => [internal] load .dockerignore
 => CACHED [1/6] FROM docker.io/library/python:3.11-slim
 => [2/6] RUN pip install --no-cache-dir uv
 => [3/6] COPY pyproject.toml ./
 => [4/6] RUN uv sync --no-dev
 => [5/6] COPY app.py ./
 => [6/6] COPY model/ ./model/
 => exporting to image
 => => naming to docker.io/library/nyc-taxi-api
```

---

### **3. Ejecutar el Contenedor**

#### **Opción A: Con Docker Run**

```bash
docker run -d \
  --name nyc-taxi-api \
  -p 8000:8000 \
  nyc-taxi-api
```

#### **Opción B: Con Docker Compose (Recomendado)**

```bash
docker-compose up -d
```

---

### **4. Verificar que Está Corriendo**

```bash
# Ver logs
docker logs nyc-taxi-api

# Ver contenedores activos
docker ps

# Health check
curl http://localhost:8000/health
```

---

## 🧪 Probar la API

Una vez corriendo, usa los mismos comandos que sin Docker:

```bash
# Health check
curl http://localhost:8000/health

# Predicción individual
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "PULocationID": 161,
    "DOLocationID": 236,
    "trip_distance": 5.2
  }'

# Documentación
open http://localhost:8000/docs
```

---

## 🛠️ Comandos Útiles

### **Ver Logs en Tiempo Real**

```bash
docker logs -f nyc-taxi-api
```

### **Detener el Contenedor**

```bash
# Con docker-compose
docker-compose down

# Con docker run
docker stop nyc-taxi-api
docker rm nyc-taxi-api
```

### **Reiniciar el Contenedor**

```bash
docker-compose restart

# O
docker restart nyc-taxi-api
```

### **Entrar al Contenedor (Debug)**

```bash
docker exec -it nyc-taxi-api bash
```

### **Ver Uso de Recursos**

```bash
docker stats nyc-taxi-api
```

---

## 🔄 Actualizar el Modelo

Cuando tengas un nuevo modelo:

```bash
# 1. Copiar nuevo modelo
uv run python copy_model.py

# 2. Reconstruir imagen
docker-compose down
docker-compose build
docker-compose up -d

# O con docker run:
docker stop nyc-taxi-api
docker rm nyc-taxi-api
docker build -t nyc-taxi-api .
docker run -d --name nyc-taxi-api -p 8000:8000 nyc-taxi-api
```

---

## 📁 Archivos Docker

```
web-service/
├── Dockerfile              # Definición de la imagen
├── docker-compose.yml      # Orquestación simple
├── .dockerignore          # Archivos a ignorar
├── app.py
├── src/
├── model/                 # ⚠️ Debe existir antes de build
└── pyproject.toml
```

---

## ✅ Resumen Rápido

```bash
# 1. Copiar modelo
uv run python copy_model.py

# 2. Construir y ejecutar
docker-compose up -d

# 3. Ver logs
docker logs -f nyc-taxi-api

# 4. Probar
curl http://localhost:8000/health

# 5. Detener
docker-compose down
```

---

## 🚀 Ventajas de Docker

- ✅ **Portabilidad**: Funciona igual en cualquier máquina
- ✅ **Aislamiento**: No afecta tu sistema
- ✅ **Reproducibilidad**: Mismo entorno siempre
- ✅ **Fácil deployment**: Sube la imagen a cualquier cloud
- ✅ **Escalabilidad**: Múltiples contenedores fácilmente

---

## 🌐 Deploy a Producción

### **Docker Hub**

```bash
# Tag
docker tag nyc-taxi-api tu-usuario/nyc-taxi-api:v1

# Push
docker push tu-usuario/nyc-taxi-api:v1
```

### **AWS ECS / Azure Container Instances / Google Cloud Run**

Usa la imagen `nyc-taxi-api` directamente en estos servicios.

---

¡Listo! That's all.
