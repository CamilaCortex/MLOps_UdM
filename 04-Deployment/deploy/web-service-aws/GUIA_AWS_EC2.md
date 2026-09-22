# Guía para Desplegar en AWS EC2 (Para Principiantes)

Esta guía te lleva desde cero -crear la instancia EC2 gratuita- hasta tener tu servicio de predicción de taxis respondiendo peticiones desde Postman.

**Importante sobre el modelo**: a diferencia de `03-Orchestration/Prefect-pipelines/models/` (que sí está excluida de git porque pesa y cambia con cada entrenamiento), los archivos del modelo "champion" ya copiados dentro de **esta** carpeta (`model/models_mlflow/` y `model/preprocessor/`) sí están versionados en git. Por eso el flujo de esta guía es simple: la instancia EC2 clona el repositorio directamente y ya tiene el modelo adentro - no hace falta subir ni descargar ninguna imagen de Docker Hub.

## 0. Antes de empezar: cuenta de AWS

Si todavía no tienes cuenta, créala en [aws.amazon.com/free](https://aws.amazon.com/free) (pide una tarjeta para verificar identidad, pero los recursos de esta guía caben dentro del Free Tier si sigues las instrucciones al pie de la letra). Si ya tienes cuenta, entra directo a la consola de EC2: [console.aws.amazon.com/ec2](https://console.aws.amazon.com/ec2/).

## 1. Crear la Instancia EC2 (Free Tier)

1. En la consola de EC2, haz clic en **Launch instance** ("Lanzar instancia").
2. **Name** ("Nombre"): ponle algo identificable, por ejemplo `taxi-prediction-api`.
3. **Application and OS Images (Amazon Machine Image)**:

   - Elige **Amazon Linux 2023 AMI**.
   - Confirma que diga la etiqueta **"Free tier eligible"** justo debajo. Esta guía asume Amazon Linux (usa el comando `yum`); si eliges Ubuntu, los comandos de instalación cambian (`apt` en vez de `yum`).
4. **Instance type** ("Tipo de instancia"): elige **t2.micro** o **t3.micro** (el que diga "Free tier eligible"). Es más que suficiente para este servicio.
5. **Key pair (login)**:

   - Haz clic en **Create new key pair**.
   - Dale un nombre (por ejemplo `taxi-api-key`).
   - Tipo: **RSA**. Formato: **.pem** (sirve para Mac, Linux y WSL en Windows; si vas a usar PuTTY nativo en Windows sin WSL, elige `.ppk`).
   - Descarga el archivo y guárdalo en un lugar que recuerdes - **AWS no te deja volver a descargarlo después**. Lo vas a necesitar en el Paso 3.
6. **Network settings** ("Configuración de red"):

   - Deja marcado **Allow SSH traffic from** y selecciona **My IP** (esto crea automáticamente la regla de entrada SSH que necesitas en el Paso 2).
   - No actives "Allow HTTP traffic" ni "Allow HTTPS traffic" - tu API va a usar el puerto 9696, esa regla la agregas aparte en el Paso 2.
   - Deja la opción de IP pública automática activada (viene así por defecto en la subred pública por defecto de la mayoría de las cuentas).
7. **Configure storage** ("Configurar almacenamiento"): deja el valor por defecto (8 GiB, tipo gp3). Está dentro del Free Tier (hasta 30 GiB) y sobra para esta imagen.
8. Haz clic en **Launch instance**.
9. Espera 1-2 minutos. En la lista de instancias, el **Instance state** debe decir **Running** y el **Status check** debe decir **2/2 checks passed** antes de seguir.
10. Haz clic en tu instancia y anota el **Public IPv4 DNS** (algo como `ec2-12-34-56-78.compute-1.amazonaws.com`). Lo vas a usar para conectarte por SSH y para configurar Postman.

## 2. Configurar el Grupo de Seguridad en AWS

El grupo de seguridad es el firewall de tu instancia. Necesitas **dos reglas de entrada**.

### Regla 1: acceso SSH (para poder conectarte a la instancia)

Si en el Paso 1.6 dejaste marcado "Allow SSH traffic from: My IP", esta regla **ya existe** - solo tienes que revisarla si más adelante no puedes conectarte:

1. Ve a la consola de EC2 y selecciona tu instancia.
2. Haz clic en el grupo de seguridad asociado (columna "Security").
3. Revisa que exista una regla de entrada:

   - Tipo: SSH
   - Puerto: 22
   - Origen: My IP (o 0.0.0.0/0 si quieres poder conectarte desde cualquier red, menos seguro)
4. Si la regla dice "My IP" pero tu IP cambió desde que la creaste (cambiaste de red, usas VPN, tu proveedor te asigna IP dinámica), edita la regla y vuelve a seleccionar "My IP" para refrescarla con tu IP actual.

### Regla 2: acceso a la API (para que Postman te llegue)

Esta sí tienes que crearla a mano:

1. En el mismo grupo de seguridad, haz clic en **Edit inbound rules** ("Editar reglas de entrada").
2. **Add rule** ("Añadir regla"):

   - Tipo: TCP personalizado
   - Rango de puertos: 9696
   - Origen: Anywhere (0.0.0.0/0)
   - Descripción: Taxi Prediction API
3. **Save rules** ("Guardar reglas").

## 3. Conectarte a tu Instancia EC2

### Requisitos previos

- La instancia ya creada (Paso 1), en estado "Running"
- El archivo `.pem` que descargaste al crear el key pair
- El DNS público de tu instancia (anotado en el Paso 1.10)

### Pasos para conectarte

1. Abre una terminal en tu computador (en Windows, la terminal de WSL).
2. Cambia los permisos de tu archivo de clave:

   ```bash
   chmod 400 tu-clave.pem
   ```
3. Conéctate a tu instancia:

   ```bash
   ssh -i tu-clave.pem ec2-user@ec2-12-34-56-78.compute-1.amazonaws.com
   ```

   Reemplaza `tu-clave.pem` con el nombre de tu archivo y la dirección con el DNS público de tu instancia. El usuario es `ec2-user` porque la AMI es Amazon Linux 2023 (con Ubuntu sería `ubuntu`, con Debian `admin`).

## 4. Instalar Docker y Git en EC2

Ya conectado a tu instancia por SSH:

```bash
# Actualizar los paquetes
sudo yum update -y

# Instalar Docker y Git
sudo yum install -y docker git

# Iniciar el servicio Docker
sudo service docker start

# Añadir tu usuario al grupo docker para no tener que usar sudo
sudo usermod -a -G docker ec2-user

# Reiniciar la sesión para aplicar el cambio de grupo
exit
```

Vuelve a conectarte con SSH como en el Paso 3.3.

## 5. Clonar el Repositorio y Construir la Imagen (en EC2)

El modelo ya viene incluido en el repositorio (ver la nota al inicio de esta guía), así que no hace falta copiar nada aparte ni instalar Python en la instancia: clonas, entras a la carpeta y construyes.

```bash
# Clonar el repositorio (es público, no necesita credenciales)
git clone https://github.com/CamilaCortex/MLOps_UdM.git

# Entrar a la carpeta de este servicio
cd MLOps_UdM/04-Deployment/deploy/web-service-aws

# Confirmar que el modelo llegó con el clone
ls model/models_mlflow/ model/preprocessor/

# Construir la imagen
docker build -t taxi-prediction-aws .
```

> Si `ls model/models_mlflow/` no muestra `MLmodel` y `model.ubj` (o `model/preprocessor/` no muestra `MLmodel` y `model.skops`), el clone no trajo el modelo - revisa la sección de Solución de Problemas.

## 6. Ejecutar el Contenedor

```bash
docker run -d -p 9696:9696 --name taxi-service taxi-prediction-aws

docker ps
docker logs -f taxi-service

# Prueba el servicio DESDE DENTRO de la instancia EC2, antes de tocar el
# grupo de seguridad o Postman. Si esto responde, el contenedor y el
# modelo ya están funcionando bien - lo que falte después es networking,
# no la aplicación.
curl http://localhost:9696/health
```

> La opción `-d` ejecuta el contenedor en segundo plano y `-p 9696:9696` mapea el puerto 9696 de la instancia EC2 (host) al puerto 9696 de adentro del contenedor. Es la misma lógica de `-p host:container` que ya conoces de probarlo en tu computador - aquí el "host" ya no es tu laptop, es la instancia EC2.
>
> Si el `curl http://localhost:9696/health` de arriba no responde, el problema está en el contenedor (revisa `docker logs taxi-service`) y todavía no tiene sentido tocar el grupo de seguridad ni Postman.

## 7. Probar el Servicio desde Postman

### Obtener la URL de tu API

```
http://ec2-12-34-56-78.compute-1.amazonaws.com:9696
```

Reemplaza `ec2-12-34-56-78.compute-1.amazonaws.com` con el DNS público de tu instancia (Paso 1.10).

### Configurar Postman

La forma más rápida es importar la colección ya lista de este mismo directorio:

1. **Importa** `NYC_Taxi_API_AWS.postman_collection.json` y `NYC_Taxi_API_AWS.postman_environment.json`.
2. **Selecciona** el environment "NYC Taxi API - AWS EC2".
3. **Edita** la variable `base_url` con el DNS público de tu instancia (reemplaza el placeholder `ec2-XX-XX-XX-XX...`).
4. **Corre** las requests "Health Check" y "Predict - Single Trip".

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

## 8. Comandos Útiles para Gestionar Docker

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

## 9. Actualizar el Modelo Desplegado

Cuando reentrenes el modelo y quieras actualizar lo que corre en EC2, el flujo es: actualizas el modelo y subes el cambio a git desde tu computador, y en EC2 solo descargas ese cambio y reconstruyes.

```bash
# En tu computador
cd 04-Deployment/deploy/web-service-aws
uv run python copy_model.py
git add model/
git commit -m "Actualizar modelo desplegado en web-service-aws"
git push
```

```bash
# En EC2
cd ~/MLOps_UdM
git pull
cd 04-Deployment/deploy/web-service-aws
docker build -t taxi-prediction-aws .
docker stop taxi-service && docker rm taxi-service
docker run -d -p 9696:9696 --name taxi-service taxi-prediction-aws
curl http://localhost:9696/health
```

## 10. Solución de Problemas

### No puedo conectarme por SSH o por el botón "Connect" de la consola

Antes de sospechar de tu clave `.pem`, revisa en este orden:

1. **Grupo de seguridad**: confirma que existe la regla SSH (puerto 22) descrita en el Paso 2, y que el origen ("My IP") sigue siendo tu IP actual.
2. **IP pública de la instancia**: en la consola, confirma que la instancia tiene una IP pública asignada (si la lanzaste sin "Auto-assign Public IP", ni SSH ni el botón "Connect" van a funcionar).
3. **Usuario correcto según la AMI**: `ec2-user` para Amazon Linux, `ubuntu` para Ubuntu, `admin` para Debian. Usar el usuario equivocado da "Permission denied (publickey)".
4. **La clave correcta**: confirma que el `.pem` que estás usando es el mismo par de llaves con el que se lanzó la instancia (si después generaste una clave nueva, esa no sirve para esta instancia).
5. **Permisos del archivo `.pem`**: debe ser `chmod 400 tu-clave.pem`; en Windows/WSL a veces el archivo hereda permisos de Windows demasiado abiertos y SSH lo rechaza directamente.

### El SSH se queda "pegado" (no da ningún error, simplemente no conecta nunca)

Si el comando `ssh -i tu-clave.pem ec2-user@...` se queda esperando indefinidamente sin ningún mensaje de error, casi siempre es la regla de SSH del grupo de seguridad bloqueando la conexión (el paquete ni siquiera llega a la instancia) - no es un problema de la clave.

**La causa más común: tu IP pública no es fija.** Muchos proveedores de internet (sobre todo en redes de universidad, wifi compartido, o si usas VPN) no asignan una IP fija por usuario: usan un conjunto de IPs y te van rotando entre ellas, a veces cada pocos minutos (esto se llama CGNAT). Si ves que la IP que AWS detectó como "Mi IP" cambia entre una consulta y otra (por ejemplo de `179.1.224.139/32` a `179.1.224.148/32` sin que hayas hecho nada), esa es la señal: para cuando guardaste la regla, tu proveedor ya te había movido a otra IP distinta.

Dos formas de resolverlo:

1. **Para este ejercicio del curso (más simple)**: cambia el origen de la regla SSH a **Anywhere (0.0.0.0/0)**, igual que la regla del puerto 9696. Esto es aceptable aquí porque Amazon Linux solo acepta login por llave `.pem`, nunca por contraseña - nadie puede entrar sin tu archivo de clave, aunque el puerto esté abierto a cualquier IP. El único costo es "ruido" de bots intentando conectarse (que van a fallar igual). Eso sí: cuando termines de probar, detén o termina la instancia en vez de dejarla corriendo expuesta indefinidamente.
2. **Para un entorno más serio**: usa **AWS Systems Manager Session Manager** en vez de SSH - te conectas a la instancia desde la consola de AWS sin necesitar el puerto 22 abierto para nada. Requiere configurar un rol de IAM adicional en la instancia, así que es un paso extra, pero elimina este problema por completo.

### El `git clone` no trae el modelo (`model/models_mlflow/` o `model/preprocessor/` vacíos o incompletos)

1. Confirma que estás clonando la rama correcta (`main`) y que el clone terminó sin errores.
2. En tu computador, confirma que el modelo SÍ está comiteado: `git ls-files 04-Deployment/deploy/web-service-aws/model` debe listar `MLmodel`, `model.ubj` (o `model.skops`) y `registered_model_meta`. Si no aparece nada, corre `uv run python copy_model.py`, luego `git add model/`, `git commit` y `git push` desde tu computador antes de volver a clonar en EC2.

### El servicio no responde

1. Verifica que el contenedor esté en ejecución:

   ```bash
   docker ps
   ```
2. Revisa los logs del contenedor:

   ```bash
   docker logs taxi-service
   ```
3. Verifica que el puerto esté abierto:

   ```bash
   sudo netstat -tulpn | grep 9696
   ```

### Error al construir la imagen Docker (en EC2)

Si encuentras errores al construir la imagen, asegúrate de que:

1. El `git clone` trajo la carpeta `model/` completa (ver el punto anterior de esta sección).
2. El archivo `Dockerfile` esté correctamente presente (`ls Dockerfile`).
3. Tienes suficiente espacio en disco:

   ```bash
   df -h
   ```

### Problemas de conexión desde Postman

1. Verifica que el grupo de seguridad permita el tráfico en el puerto 9696 (Paso 2, Regla 2).
2. Prueba la conexión con curl desde tu máquina local:

   ```bash
   curl -X POST http://ec2-12-34-56-78.compute-1.amazonaws.com:9696/predict \
        -H "Content-Type: application/json" \
        -d '{"PULocationID": 161, "DOLocationID": 236, "trip_distance": 2.5}'
   ```

### Error al cargar el modelo dentro del contenedor (versión incompatible de scikit-learn / xgboost / skops)

Revisa `README.md` -sección Troubleshooting- para el procedimiento completo: hay que revisar `model/preprocessor/requirements.txt` y `model/models_mlflow/requirements.txt` (si existen localmente), ajustar `pyproject.toml` y reconstruir la imagen.
