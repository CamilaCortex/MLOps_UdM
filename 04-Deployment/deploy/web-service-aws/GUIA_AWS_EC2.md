# Guía para Desplegar en AWS EC2 (Para Principiantes)

Esta guía te ayudará a desplegar tu servicio de predicción de taxis en un servidor AWS EC2 y configurarlo para recibir solicitudes desde Postman.

**Importante sobre el modelo**: el modelo (XGBoost `.ubj`) y el preprocessor (`skops`) están excluidos de git a propósito (pesan y cambian con cada entrenamiento), así que la instancia EC2 no los puede obtener con un simple `git clone`. Por eso el flujo de esta guía es: construyes la imagen Docker **en tu computador** (con el modelo ya adentro), la subes a Docker Hub, y en EC2 solo la descargas y la corres.

## 0. Construir la Imagen con el Modelo (en tu computador)

Antes de tocar EC2, desde tu computador:

```bash
cd 04-Deployment/deploy/web-service-aws

# Copia el modelo "champion" actual desde MLflow
uv run python copy_model.py

# Construye la imagen con el modelo ya incluido
docker build -t taxi-prediction-aws .

# Pruébala en local antes de subirla
docker run -d -p 9696:9696 --name taxi-prediction-aws taxi-prediction-aws
curl http://localhost:9696/health
docker stop taxi-prediction-aws && docker rm taxi-prediction-aws
```

## 1. Subir la Imagen a Docker Hub

```bash
# Inicia sesión (una sola vez)
docker login

# Etiqueta la imagen con tu usuario de Docker Hub
docker tag taxi-prediction-aws tu-usuario/taxi-prediction-aws:v1

# Sube la imagen
docker push tu-usuario/taxi-prediction-aws:v1
```

> Reemplaza `tu-usuario` por tu usuario real de Docker Hub. El repositorio puede ser público o privado (si es privado, en el Paso 4 necesitarás hacer `docker login` también en la instancia EC2).

## 2. Conectarte a tu Instancia EC2

### Requisitos previos

- Una instancia EC2 ya creada en AWS
- El archivo `.pem` de tu clave privada
- El DNS público de tu instancia (algo como `ec2-12-34-56-78.compute-1.amazonaws.com`)

### Pasos para conectarte

1. **Abre una terminal en tu computadora**
2. **Cambia los permisos de tu archivo de clave**:

   ```bash
   chmod 400 tu-clave.pem
   ```
3. **Conéctate a tu instancia EC2**:

   ```bash
   ssh -i tu-clave.pem ec2-user@ec2-12-34-56-78.compute-1.amazonaws.com
   ```

   Reemplaza `tu-clave.pem` con el nombre de tu archivo de clave y la dirección con el DNS público de tu instancia.

## 3. Instalar Docker en EC2

Una vez conectado a tu instancia EC2, instala Docker:

```bash
# Actualizar los paquetes
sudo yum update -y

# Instalar Docker
sudo yum install -y docker

# Iniciar el servicio Docker
sudo service docker start

# Añadir tu usuario al grupo docker para no tener que usar sudo
sudo usermod -a -G docker ec2-user

# Reiniciar la sesión para aplicar los cambios de grupo
exit
```

Vuelve a conectarte a la instancia con SSH como en el paso 2.3.

## 4. Descargar y Ejecutar el Contenedor en EC2

Ya no hace falta clonar el repositorio ni instalar Python en la instancia: solo se descarga la imagen que ya tiene el modelo adentro.

```bash
# Descargar la imagen desde Docker Hub
docker pull tu-usuario/taxi-prediction-aws:v1

# Ejecutar el contenedor
docker run -d -p 9696:9696 --name taxi-service tu-usuario/taxi-prediction-aws:v1

docker ps
docker logs -f taxi-service
```

> La opción `-d` ejecuta el contenedor en segundo plano y `-p 9696:9696` mapea el puerto 9696 del contenedor al puerto 9696 de la instancia EC2.

## 5. Configurar el Grupo de Seguridad en AWS

Para permitir el tráfico externo a tu aplicación:

1. **Ve a la consola de AWS** y selecciona tu instancia EC2
2. **Haz clic en el grupo de seguridad** asociado a tu instancia
3. **Añade una regla de entrada**:

   - Tipo: TCP personalizado
   - Rango de puertos: 9696
   - Origen: Anywhere (0.0.0.0/0)
   - Descripción: Taxi Prediction API
4. **Guarda los cambios**

## 6. Probar el Servicio desde Postman

### Obtener la URL de tu API

La URL de tu API será:

```
http://ec2-12-34-56-78.compute-1.amazonaws.com:9696
```

Reemplaza `ec2-12-34-56-78.compute-1.amazonaws.com` con el DNS público de tu instancia EC2.

### Configurar Postman

La forma más rápida es importar la colección ya lista de este mismo directorio:

1. **Importa** `NYC_Taxi_API_AWS.postman_collection.json` y `NYC_Taxi_API_AWS.postman_environment.json`
2. **Selecciona** el environment "NYC Taxi API - AWS EC2"
3. **Edita** la variable `base_url` con el DNS público de tu instancia (reemplaza el placeholder `ec2-XX-XX-XX-XX...`)
4. **Corre** las requests "Health Check" y "Predict - Single Trip"

O manualmente, creando las requests tú misma:

- Health check: `GET http://ec2-12-34-56-78.compute-1.amazonaws.com:9696/health`
- Predicción: `POST http://ec2-12-34-56-78.compute-1.amazonaws.com:9696/predict`, header `Content-Type: application/json`, body:

  ```json
  {
    "PULocationID": 161,
    "DOLocationID": 236,
    "trip_distance": 2.5
  }
  ```

  Respuesta esperada:

  ```json
  {
    "duration": 7.42,
    "pickup_location": 161,
    "dropoff_location": 236,
    "trip_distance": 2.5,
    "model_name": "nyc-taxi-duration-predictor",
    "model_version": "2"
  }
  ```

## 7. Comandos Útiles para Gestionar Docker

```bash
# Ver contenedores en ejecución
docker ps

# Ver logs del contenedor
docker logs taxi-service
docker logs -f taxi-service   # en tiempo real

# Detener el contenedor
docker stop taxi-service

# Iniciar el contenedor detenido
docker start taxi-service

# Eliminar el contenedor (debe estar detenido primero)
docker rm taxi-service
```

## 8. Actualizar el Modelo Desplegado

Cuando reentrenes el modelo y quieras actualizar lo que corre en EC2, repite el flujo desde tu computador (no en EC2):

```bash
# En tu computador
cd 04-Deployment/deploy/web-service-aws
uv run python copy_model.py
docker build -t taxi-prediction-aws .
docker tag taxi-prediction-aws tu-usuario/taxi-prediction-aws:v2
docker push tu-usuario/taxi-prediction-aws:v2
```

```bash
# En EC2
docker pull tu-usuario/taxi-prediction-aws:v2
docker stop taxi-service && docker rm taxi-service
docker run -d -p 9696:9696 --name taxi-service tu-usuario/taxi-prediction-aws:v2
```

## 9. Solución de Problemas

### El servicio no responde

1. **Verifica que el contenedor esté en ejecución**:

   ```bash
   docker ps
   ```
2. **Revisa los logs del contenedor**:

   ```bash
   docker logs taxi-service
   ```
3. **Verifica que el puerto esté abierto**:

   ```bash
   sudo netstat -tulpn | grep 9696
   ```

### Error al construir la imagen Docker (en tu computador)

Si encuentras errores al construir la imagen, asegúrate de que:

1. Corriste `uv run python copy_model.py` y existe la carpeta `model/` con `model/models_mlflow/` y `model/preprocessor/`
2. El archivo `Dockerfile` esté correctamente configurado
3. Tienes suficiente espacio en disco:

   ```bash
   df -h
   ```

### `docker pull` falla en EC2 con "repository does not exist" o "unauthorized"

- Confirma que el nombre de la imagen en `docker pull` coincide exactamente con el que usaste en `docker push` (usuario, nombre y tag)
- Si el repositorio en Docker Hub es privado, primero corre `docker login` en la instancia EC2

### Problemas de conexión desde Postman

1. **Verifica que el grupo de seguridad** permita el tráfico en el puerto 9696
2. **Prueba la conexión** con curl desde tu máquina local:

   ```bash
   curl -X POST http://ec2-12-34-56-78.compute-1.amazonaws.com:9696/predict \
        -H "Content-Type: application/json" \
        -d '{"PULocationID": 161, "DOLocationID": 236, "trip_distance": 2.5}'
   ```

### Error al cargar el modelo dentro del contenedor (versión incompatible de scikit-learn / xgboost / skops)

Revisa `README.md` -sección Troubleshooting- para el procedimiento completo: hay que revisar `model/preprocessor/requirements.txt` y `model/models_mlflow/requirements.txt`, ajustar `pyproject.toml` y reconstruir la imagen.
