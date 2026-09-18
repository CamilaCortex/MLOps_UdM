# Imagen base de Python (misma versión que .python-version / pyproject.toml)
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
# entrenado (ver model/models_mlflow/requirements.txt y
# model/preprocessor/requirements.txt para la versión exacta que declaró
# MLflow al guardarlo).
RUN uv sync --no-dev

# Copiar el código fuente de la aplicación
COPY app.py ./
COPY src/ ./src/
COPY templates/ ./templates/

# Copiar el modelo (debe existir antes del build: ver copy_model.py /
# "uv run python copy_model.py" en el README)
COPY model/ ./model/

# Exponer el puerto donde escucha la API
EXPOSE 8000

# Variable de entorno para que los logs de Python salgan sin buffer
ENV PYTHONUNBUFFERED=1

# Comando para iniciar la API dentro del entorno que uv acaba de crear
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
