# Imagen base de Python
FROM python:3.11-slim

# Instalar UV
RUN pip install --no-cache-dir uv

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY pyproject.toml ./

# Instalar dependencias
RUN uv sync --no-dev

# Copiar código fuente
COPY app.py ./
COPY src/ ./src/
COPY config/ ./config/

# Copiar modelo (debe existir antes de build)
COPY model/ ./model/

# Exponer puerto
EXPOSE 8000

# Comando para iniciar la API
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
