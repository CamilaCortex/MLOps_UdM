FROM python:3.11.9-slim

# Actualizar pip e instalar UV
RUN pip install -U pip
RUN pip install uv

WORKDIR /app

# Copiar solo el archivo de dependencias
COPY [ "pyproject.toml", "./" ]

# Instalar dependencias con UV
RUN uv pip install --system -e .

# Copiar solo los archivos necesarios para la aplicación
COPY [ "predict.py", "lin_reg.bin", "./" ]

# Exponer puerto
EXPOSE 9696

# Ejecutar la aplicación con gunicorn
ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]