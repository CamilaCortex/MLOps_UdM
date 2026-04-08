"""
🐱 Gatitos App - Versión Local (sin Docker)
Una aplicación simple de FastAPI que muestra fotos aleatorias de gatitos
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random

app = FastAPI(title="Gatitos App", version="1.0.0")
templates = Jinja2Templates(directory="templates")

# Lista de URLs de gatitos de la API pública Cat as a Service
GATITOS = [
    "https://cataas.com/cat",
    "https://cataas.com/cat/cute",
    "https://cataas.com/cat/says/Hello",
    "https://cataas.com/cat/says/Python",
    "https://cataas.com/cat/says/Meow",
]

@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    """Página principal con un gatito aleatorio"""
    gatito_url = random.choice(GATITOS)
    return templates.TemplateResponse(request=request, name='index.html', context={'gatito_url': gatito_url})

@app.get('/health')
def health():
    """Endpoint de salud para verificar que la app está corriendo"""
    return {'status': 'healthy', 'message': '🐱 Gatitos app is running!'}

if __name__ == '__main__':
    import uvicorn
    print("🐱 Iniciando Gatitos App...")
    print("📍 Abre tu navegador en: http://127.0.0.1:5000")
    print("⏹️  Para detener: Ctrl+C")
    uvicorn.run(app, host='127.0.0.1', port=5000)


# uv run python app.py