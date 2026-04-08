"""
🐱 Gatitos App - Versión Docker
Una aplicación simple de FastAPI que muestra fotos aleatorias de gatitos
Optimizada para correr en contenedores Docker
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random

app = FastAPI(title="Gatitos App Docker", version="1.0.0")
templates = Jinja2Templates(directory="templates")

# Lista de URLs de gatitos de la API pública Cat as a Service
GATITOS = [
    "https://cataas.com/cat",
    "https://cataas.com/cat/cute",
    "https://cataas.com/cat/says/Hello",
    "https://cataas.com/cat/says/Docker",
    "https://cataas.com/cat/says/Meow",
]

@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    """Página principal con un gatito aleatorio"""
    gatito_url = random.choice(GATITOS)
    # Usar el template específico para Docker
    return templates.TemplateResponse(request=request, name='index_docker.html', context={'gatito_url': gatito_url})

@app.get('/health')
def health():
    """Endpoint de salud para verificar que la app está corriendo"""
    return {'status': 'healthy', 'message': '🐱 Gatitos app is running in Docker!'}

if __name__ == '__main__':
    import uvicorn
    # Importante: host='0.0.0.0' para que Docker pueda acceder desde fuera del contenedor
    print("🐳 Iniciando Gatitos App en Docker...")
    print("📍 La app estará disponible en el puerto mapeado")
    uvicorn.run(app, host='0.0.0.0', port=5000)


# http://localhost:8080