# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY pyproject.toml ./

# Instalar dependencias directamente con pip
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn[standard]==0.32.0 \
    pydantic==2.9.2 \
    mlflow==2.17.2 \
    xgboost==2.1.2 \
    scikit-learn==1.5.2

# Copiar código fuente
COPY app.py ./
COPY src/ ./src/
COPY templates/ ./templates/

# Copiar modelo (debe existir antes de build)
COPY model/ ./model/

# Exponer puerto
EXPOSE 8000

# Comando para iniciar la API
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
