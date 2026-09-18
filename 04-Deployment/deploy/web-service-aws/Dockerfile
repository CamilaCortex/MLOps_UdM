# Imagen base de Python (misma versión que pyproject.toml)
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar uv: el mismo gestor de dependencias que se usa en todo el
# proyecto, para no duplicar versiones a mano en dos lugares distintos
# (pyproject.toml es la única fuente de verdad de las dependencias).
RUN pip install --no-cache-dir uv

# Copiar solo el archivo de dependencias primero (aprovecha el cache de
# Docker: si el código cambia pero no las dependencias, este paso no se
# repite).
COPY pyproject.toml ./

# Instalar las dependencias declaradas en pyproject.toml -incluye mlflow,
# xgboost, scikit-learn y skops en las versiones compatibles con el modelo
# entrenado.
RUN uv sync --no-dev

# Copiar el código fuente de la aplicación
COPY predict.py ./
COPY src/ ./src/

# Copiar el modelo (debe existir ANTES de este build: correr primero
# "uv run python copy_model.py" en tu máquina -ver README.md/
# GUIA_AWS_EC2.md-. Esta imagen se construye localmente CON el modelo ya
# adentro, porque EC2 no tiene acceso al registro de MLflow ni al
# directorio 03-Orchestration/Prefect-pipelines/models/, que está
# excluido de git).
COPY model/ ./model/

# Exponer el puerto donde escucha la API
EXPOSE 9696

# Variable de entorno para que los logs de Python salgan sin buffer
ENV PYTHONUNBUFFERED=1

# Ejecutar la aplicación con gunicorn, usando el entorno que uv acaba de
# crear
CMD ["uv", "run", "gunicorn", "--bind=0.0.0.0:9696", "predict:app"]
