# Guía para Desplegar Docker en AWS EC2 (Para Principiantes)

Esta guía te ayudará a desplegar tu servicio de predicción de taxis en un servidor AWS EC2 y configurarlo para recibir solicitudes desde Postman.

## 1. Conectarse a tu Instancia EC2

### Requisitos previos

- Una instancia EC2 ya creada en AWS
- El archivo .pem de tu clave privada
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

   > 💡 Reemplaza `tu-clave.pem` con el nombre de tu archivo de clave y la dirección con el DNS público de tu instancia.
   >

## 2. Instalar Docker en EC2

Una vez conectado a tu instancia EC2, instala Docker:

```bash
# Actualizar los paquetes
sudo yum update -y

# Instalar Docker
sudo yum install -y docker

# Install git
sudo yum install -y git

# Iniciar el servicio Docker
sudo service docker start

# Añadir tu usuario al grupo docker para no tener que usar sudo
sudo usermod -a -G docker ec2-user

# Reiniciar la sesión para aplicar los cambios de grupo
exit
```

Vuelve a conectarte a la instancia con SSH como en el paso 1.3.

## 3. Clonar el Repositorio

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/tu-repositorio.git

# Entrar al directorio
cd tu-repositorio/04-Deployment/deploy/web-service-docker
```

## 4. Construir y Ejecutar el Contenedor Docker

```bash

# Construir la imagen Docker
docker build -t taxi-prediction .

# Ejecutar el contenedor
docker run -d -p 9696:9696 --name taxi-service taxi-prediction

docker ps

docker logs -f taxi-service

docker inspect taxi-service


```

> 💡 La opción `-d` ejecuta el contenedor en segundo plano y `-p 9696:9696` mapea el puerto 9696 del contenedor al puerto 9696 de la instancia EC2.

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

> 💡 Reemplaza `ec2-12-34-56-78.compute-1.amazonaws.com` con el DNS público de tu instancia EC2.

### Configurar Postman

1. **Abre Postman** en tu computadora
2. **Crea una nueva solicitud**:

   - Método: POST
   - URL: `http://ec2-12-34-56-78.compute-1.amazonaws.com:9696/predict`
   - Headers: Content-Type: application/json
3. **Añade el cuerpo de la solicitud**:

   ```json
   {
     "PULocationID": 161,
     "DOLocationID": 236,
     "trip_distance": 2.5
   }
   ```
4. **Envía la solicitud** y deberías recibir una respuesta como:

   ```json
   {
     "duration": 12.34,
     "pickup_location": 161,
     "dropoff_location": 236,
     "trip_distance": 2.5
   }
   ```

## 7. Comandos Útiles para Gestionar Docker

```bash
# Ver contenedores en ejecución
docker ps

# Ver logs del contenedor
docker logs taxi-service

# Detener el contenedor
docker stop taxi-service

# Iniciar el contenedor detenido
docker start taxi-service

# Eliminar el contenedor (debe estar detenido primero)
docker rm taxi-service
```

## 8. Solución de Problemas

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

### Error al construir la imagen Docker

Si encuentras errores al construir la imagen, asegúrate de que:

1. El archivo `lin_reg.bin` esté en el directorio
2. El archivo `Dockerfile` esté correctamente configurado
3. Tienes suficiente espacio en disco:
   ```bash
   df -h
   ```

### Problemas de conexión desde Postman

1. **Verifica que el grupo de seguridad** permita el tráfico en el puerto 9696
2. **Prueba la conexión** con curl desde tu máquina local:
   ```bash
   curl -X POST http://ec2-12-34-56-78.compute-1.amazonaws.com:9696/predict \
        -H "Content-Type: application/json" \
        -d '{"PULocationID": 161, "DOLocationID": 236, "trip_distance": 2.5}'
   ```
