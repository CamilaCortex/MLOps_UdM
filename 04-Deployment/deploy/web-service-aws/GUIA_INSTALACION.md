# Guía de Instalación - Servicio de Predicción con Docker

Este documento proporciona instrucciones paso a paso para configurar y ejecutar el servicio de predicción de duración de viajes en taxi, tanto en modo local como con Docker.

## 1. Instalación de Requisitos Previos

### Python 3.11.9

#### En Windows

1. **Instalar pyenv-win**:

   ```powershell
   # Usando PowerShell
   Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"
   ./install-pyenv-win.ps1
   ```

2. **Reiniciar la terminal** y luego instalar Python 3.11.9:

   ```cmd
   pyenv install 3.11.9
   pyenv global 3.11.9
   ```

3. **Verificar la instalación**:

   ```cmd
   python --version
   ```

#### En macOS

1. **Instalar pyenv** con Homebrew:

   ```bash
   brew install pyenv
   ```

2. **Configurar pyenv** en tu shell (añade esto a tu .zshrc o .bash_profile):

   ```bash
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
   echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
   echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
   ```

3. **Reiniciar la terminal** y luego instalar Python 3.11.9:

   ```bash
   pyenv install 3.11.9
   pyenv global 3.11.9
   ```

4. **Verificar la instalación**:

   ```bash
   python --version
   ```

### UV (Gestor de Paquetes)

#### En Windows y macOS

1. **Instalar UV**:

   ```bash
   pip install uv
   ```

2. **Verificar la instalación**:

   ```bash
   uv --version
   ```

### Docker (Opcional, para contenedores)

#### En Windows

1. Descargar e instalar [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop)
2. Seguir el asistente de instalación
3. Verificar: `docker --version`

#### En macOS

1. Descargar e instalar [Docker Desktop para Mac](https://www.docker.com/products/docker-desktop)
2. Seguir el asistente de instalación
3. Verificar: `docker --version`

## 2. Configuración del Proyecto

### Clonar o Descargar el Repositorio

```bash
# Si usas Git
git clone <URL_DEL_REPOSITORIO>
cd web-service-docker
```

### Preparar el Archivo del Modelo

Asegúrate de tener el archivo del modelo en el directorio del proyecto:

```bash
# Copiar desde el directorio web-service original si es necesario
cp ../web-service/lin_reg.bin .
```

## 3. Configuración del Entorno Virtual

### Crear y Activar el Entorno Virtual con UV

```bash
# Crear el entorno virtual
uv venv

# Activar el entorno virtual
# En Windows:
.venv\Scripts\activate

# En macOS/Linux:
source .venv/bin/activate
```

### Instalar Dependencias

```bash
# Instalar dependencias del proyecto
uv pip install -e .
```

## 4. Ejecutar la Aplicación

### Opción 1: Ejecutar con Python directamente

```bash
# Usando UV sin activar el entorno virtual
uv run python predict.py

# O si ya has activado el entorno virtual
python predict.py
```

### Opción 2: Ejecutar con Gunicorn (recomendado para producción)

```bash
# Usando UV sin activar el entorno virtual
uv run gunicorn --bind 0.0.0.0:9696 predict:app

# O si ya has activado el entorno virtual
gunicorn --bind 0.0.0.0:9696 predict:app
```

## 5. Probar la Aplicación

### Verificar que el Servicio está Funcionando

Abre otra terminal y ejecuta:

```bash
curl http://localhost:9696/health
```

Debes recibir una respuesta como:

```json
{"status": "healthy"}
```

### Realizar una Predicción de Prueba

```bash
curl -X POST http://localhost:9696/predict \
     -H "Content-Type: application/json" \
     -d '{"PULocationID": 161, "DOLocationID": 236, "trip_distance": 2.5}'
```

Debes recibir una respuesta como:

```json
{
  "duration": 12.34,
  "pickup_location": 161,
  "dropoff_location": 236,
  "trip_distance": 2.5
}
```

### Ejecutar el Script de Prueba

```bash
# Usando UV
uv run python test.py

# O si ya has activado el entorno virtual
python test.py
```

## 6. Uso con Docker

### Construir la Imagen Docker

```bash
docker build -t taxi-prediction .
```

### Ejecutar el Contenedor

```bash
docker run -p 9696:9696 taxi-prediction
```

### Probar el Servicio en Docker

```bash
# Verificar el estado
curl http://localhost:9696/health

# Realizar una predicción
curl -X POST http://localhost:9696/predict \
     -H "Content-Type: application/json" \
     -d '{"PULocationID": 161, "DOLocationID": 236, "trip_distance": 2.5}'
```

## 7. Solución de Problemas Comunes

### Error: Puerto en uso

Si ves un error como "Address already in use":

```bash
# Encontrar el proceso que usa el puerto
lsof -i :9696

# Terminar ese proceso
kill -9 [PID]
```

### Error: Modelo no encontrado

Si la aplicación no puede encontrar el modelo:

```bash
# Copiar el modelo desde el directorio original
cp ../web-service/lin_reg.bin .
```

### Error: Gunicorn no encontrado

Si recibes "command not found: gunicorn":

```bash
# Asegurarte de que el entorno virtual está activado
source .venv/bin/activate  # En macOS/Linux
.venv\Scripts\activate     # En Windows

# O instalar gunicorn directamente
uv pip install gunicorn
```

### Error: Dependencias faltantes

Si hay errores de módulos no encontrados:

```bash
# Sincronizar todas las dependencias
uv pip sync

# O instalar dependencias específicas
uv pip install flask scikit-learn gunicorn
```
