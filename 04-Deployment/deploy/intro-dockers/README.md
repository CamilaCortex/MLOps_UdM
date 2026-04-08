# Práctica de Docker - App de Gatitos

Aprende Docker desde cero creando y dockerizando una aplicación web que muestra fotos aleatorias de gatitos.

## Objetivos

1. Ejecutar una app web local
2. Entender qué es Docker y para qué sirve
3. Crear un Dockerfile
4. Construir una imagen Docker
5. Ejecutar un contenedor
6. Comparar local vs Docker

---

## Estructura del Proyecto

```
practica-gatitos/
├── app.py              # App LOCAL (versión simple)
├── app_docker.py       # App DOCKER (optimizada para contenedores)
├── requirements.txt    # Dependencias: FastAPI + Uvicorn
├── Dockerfile          # Instrucciones para crear la imagen
├── .dockerignore       # Archivos a ignorar
├── templates/
│   ├── index.html         # Template para versión local
│   └── index_docker.html  # Template para versión Docker
└── README.md           # Esta guía
```

---

# PARTE 1: App Local (Sin Docker)

## ¿Por Qué Empezar Sin Docker?

Para entender **qué problemas resuelve Docker**, primero necesitamos experimentar los problemas de una app local.

## Paso 1: Verificar Python

```bash
python --version
# Debe ser Python 3.8 o superior
```

## Paso 2: Ir al Directorio

```bash
cd MLOps_UdM/04-Deployment/deploy/intro-dockers
```

## Paso 3: Instalar Dependencias

```bash
# Con uv (recomendado) - Usa comillas para evitar error en zsh
uv add fastapi "uvicorn[standard]" jinja2

# O con pip
pip install -r requirements.txt
```

> **Nota para usuarios de zsh:** Si usas zsh (shell por defecto en Mac), debes usar comillas alrededor de `uvicorn[standard]` para evitar el error "no matches found".

## Paso 4: Ejecutar la App Local

```bash
uv run python app.py
```

**Salida esperada**:
```
Iniciando Gatitos App...
Abre tu navegador en: http://127.0.0.1:5000
Para detener: Ctrl+C
 * Running on http://127.0.0.1:5000
```

## Paso 5: Abrir en el Navegador

Abre: **http://127.0.0.1:5000**

Deberías ver:
- Foto aleatoria de un gatito
- Badge verde "Corriendo Localmente"
- Botón "Otro gatito"
- Texto "¡Aplicación web con FastAPI!"

## Paso 6: Probar la App

1. Click en "Otro gatito" → Cambia la imagen
2. Recarga la página → Otro gatito diferente
3. Ir a http://127.0.0.1:5000/health → Ver endpoint de salud

## Paso 7: Detener la App

Presiona `Ctrl+C` en la terminal

---

## Problemas de la App Local

| Problema | Descripción |
|----------|-------------|
| **Dependencias** | Necesitas instalar FastAPI y Uvicorn manualmente |
| **Versiones** | ¿Qué pasa si otro proyecto necesita otras versiones? |
| **Portabilidad** | En otra computadora, ¿funcionará igual? |
| **Configuración** | Necesitas Python instalado |
| **"En mi máquina funciona"** | Clásico problema de desarrollo |

**Docker resuelve todos estos problemas.**

---

# PARTE 2: Dockerizar la App

## ¿Qué es Docker?

Docker es una plataforma que permite **empaquetar** una aplicación con todas sus dependencias en un **contenedor** que puede ejecutarse en cualquier lugar.

### Conceptos Clave

- **Imagen**: Plantilla con todo lo necesario (código + dependencias)
- **Contenedor**: Instancia en ejecución de una imagen
- **Dockerfile**: Receta para crear una imagen

## Paso 1: Verificar Docker

```bash
docker --version
```

Deberías ver algo como: `Docker version 28.5.1`

Si no tienes Docker instalado, consulta `GUIA_INSTALACION_DOCKER.md`

## Paso 2: Entender el Dockerfile

Abre el archivo `Dockerfile` y revisa cada línea:

```dockerfile
# Imagen base: Python ya instalado
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar FastAPI y dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la app
COPY app_docker.py app.py
COPY templates/ templates/

# Exponer el puerto 5000 (donde corre FastAPI)
EXPOSE 5000

# Variable de entorno para Python
ENV PYTHONUNBUFFERED=1

# Comando para iniciar la app con uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

**Explicación**:
1. `FROM`: Usamos Python 3.11 como base
2. `WORKDIR`: Creamos carpeta `/app` en el contenedor
3. `COPY requirements.txt`: Copiamos solo dependencias primero
4. `RUN pip install`: Instalamos FastAPI, Uvicorn y Jinja2
5. `COPY app_docker.py`: Copiamos el código
6. `EXPOSE 5000`: Documentamos el puerto
7. `CMD`: Comando para ejecutar la app con uvicorn

## Paso 3: Construir la Imagen

```bash
docker build -t gatitos-app .
```

**Explicación**:
- `docker build`: Construir imagen
- `-t gatitos-app`: Nombre (tag) de la imagen
- `.`: Usar Dockerfile en directorio actual

**Salida esperada** (~30-60 segundos):
```
[+] Building 15.2s (11/11) FINISHED
 => [1/7] FROM docker.io/library/python:3.11-slim
 => [2/7] WORKDIR /app
 => [3/7] COPY requirements.txt .
 => [4/7] RUN pip install --no-cache-dir -r requirements.txt
 => [5/7] COPY app_docker.py app.py
 => [6/7] COPY templates/ templates/
 => exporting to image
 => => naming to docker.io/library/gatitos-app
```

### 💡 Build con Cache vs Sin Cache

#### CON Cache (Por Defecto - Recomendado)

```bash
docker build -t gatitos-app .
```

**Qué hace**: Reutiliza capas que no han cambiado.

**Ventajas**:
- ⚡ Muy rápido (0.2-2 segundos)
- 💾 No descarga Python de nuevo
- 🎯 No reinstala Flask si no cambió

**Cuándo usar**:
- Desarrollo diario
- Solo cambiaste código Python
- Quieres iterar rápido

**Salida típica**:
```
=> CACHED [4/6] RUN pip install ...  ← No reinstala
Total: 0.2 segundos ⚡
```

#### SIN Cache (Solo Casos Especiales)

```bash
docker build --no-cache -t gatitos-app .
```

**Qué hace**: Reconstruye TODO desde cero.

**Ventajas**:
- ✅ Build limpia garantizada
- ✅ Elimina problemas de cache corrupto
- ✅ Recomendado antes de producción

**Cuándo usar**:
- Hay un bug extraño
- Antes de desplegar a producción
- Cambiaste `requirements.txt`

**Salida típica**:
```
=> [4/6] RUN pip install ...  15.0s ← Reinstala todo
Total: 45 segundos 🐌
```

**Regla de oro**: Usa CON cache (99% del tiempo). Solo usa SIN cache cuando tengas dudas o vayas a producción.

## Paso 4: Verificar la Imagen

```bash
docker images
```

**Salida esperada**:
```
REPOSITORY     TAG       IMAGE ID       CREATED          SIZE
gatitos-app    latest    abc123def456   10 seconds ago   150MB
```

## Paso 5: Ejecutar el Contenedor

```bash
docker run -d -p 8080:5000 --name mi-gatitos gatitos-app
```

**Explicación**:
- `docker run`: Ejecutar contenedor
- `-d`: Modo detached (segundo plano)
- `-p 8080:5000`: Mapear puerto 8080 (tu PC) → 5000 (contenedor)
- `--name mi-gatitos`: Nombre del contenedor
- `gatitos-app`: Imagen a usar

**Salida esperada**:
```
a1b2c3d4e5f6789...  (ID del contenedor)
```

## Paso 6: Verificar que Está Corriendo

```bash
docker ps
```

**Salida esperada**:
```
CONTAINER ID   IMAGE         COMMAND           CREATED         STATUS         PORTS                    NAMES
a1b2c3d4e5f6   gatitos-app   "python app.py"   5 seconds ago   Up 4 seconds   0.0.0.0:8080->5000/tcp   mi-gatitos
```

## Paso 7: Abrir en el Navegador

Abre: **http://localhost:8080**

Deberías ver:
- 🐱 Foto aleatoria de un gatito
- 🐳 Badge azul "Corriendo en Docker"
- Fondo azul (diferente al local)
- Información sobre Docker

## Paso 8: Ver Logs del Contenedor

```bash
docker logs mi-gatitos
```

**Salida esperada**:
```
🐳 Iniciando Gatitos App en Docker...
📍 La app estará disponible en el puerto mapeado
 * Running on http://0.0.0.0:5000
```

## Paso 9: Ver Estadísticas en Tiempo Real

```bash
docker stats mi-gatitos
```

Presiona `Ctrl+C` para salir

## Paso 10: Detener el Contenedor

```bash
docker stop mi-gatitos
```

## Paso 11: Eliminar el Contenedor

```bash
docker rm mi-gatitos
```

---

# 📊 PARTE 3: Comparación Local vs Docker

## Tabla Comparativa

| Aspecto | Local | Docker |
|---------|-------|--------|
| **Comando para ejecutar** | `python app.py` | `docker run ...` |
| **Puerto** | 5000 | 8080 → 5000 |
| **Dependencias** | Instalar manualmente | Incluidas en la imagen |
| **Python** | Necesitas instalarlo | Ya incluido |
| **Portabilidad** | ❌ Depende del sistema | ✅ Funciona en cualquier lado |
| **Aislamiento** | ❌ Comparte con el sistema | ✅ Totalmente aislado |
| **Reproducibilidad** | ❌ Puede variar | ✅ Siempre igual |
| **Tamaño** | ~50 MB (solo código) | ~150 MB (todo incluido) |
| **Inicio** | Rápido (~1s) | Medio (~3s) |

## Diferencias Visuales

### App Local
- 💻 Badge verde "Corriendo Localmente"
- Fondo morado
- Puerto: 5000

### App Docker
- 🐳 Badge azul "Corriendo en Docker"
- Fondo azul
- Puerto: 8080

## Ventajas de Docker

1. **✅ Portabilidad**: Funciona igual en Mac, Windows, Linux
2. **✅ Aislamiento**: No afecta otras apps ni el sistema
3. **✅ Reproducibilidad**: Mismo resultado siempre
4. **✅ Fácil de compartir**: Solo necesitas la imagen
5. **✅ Escalabilidad**: Fácil crear múltiples instancias
6. **✅ Versionado**: Puedes tener múltiples versiones
7. **✅ CI/CD**: Integración continua simplificada

## Cuándo Usar Docker

✅ **Usa Docker cuando**:
- Trabajas en equipo
- Despliegas en producción
- Necesitas consistencia entre ambientes
- Quieres aislar dependencias
- Trabajas con microservicios

❌ **No necesitas Docker para**:
- Scripts simples de una sola vez
- Desarrollo muy rápido/prototipos
- Aprendizaje básico de Python

---

# 🎓 Ejercicios Prácticos

## Ejercicio 1: Ejecutar Ambas Versiones Simultáneamente

```bash
# Terminal 1: App local
uv run python app.py
# Abre: http://127.0.0.1:5000

# Terminal 2: App Docker
docker run -d -p 8080:5000 --name gatitos-docker gatitos-app
# Abre: http://localhost:8080

# Compara las dos versiones lado a lado
```

## Ejercicio 2: Múltiples Contenedores

```bash
# Crear 3 contenedores
docker run -d -p 8080:5000 --name gatitos-1 gatitos-app
docker run -d -p 8081:5000 --name gatitos-2 gatitos-app
docker run -d -p 8082:5000 --name gatitos-3 gatitos-app

# Abrir en el navegador:
# http://localhost:8080
# http://localhost:8081
# http://localhost:8082

# Cada uno muestra gatitos diferentes!
```

## Ejercicio 3: Inspeccionar el Contenedor

```bash
# Ver detalles del contenedor
docker inspect mi-gatitos

# Ejecutar comando dentro del contenedor
docker exec -it mi-gatitos bash

# Dentro del contenedor:
ls -la
cat app.py
exit
```

## Ejercicio 4: Modificar y Reconstruir

1. Modifica `app_docker.py` (agrega más URLs de gatitos)
2. Reconstruye la imagen: `docker build -t gatitos-app:v2 .`
3. Ejecuta la nueva versión: `docker run -d -p 8080:5000 --name gatitos-v2 gatitos-app:v2`

---

# 🔧 Comandos Docker Útiles

## Gestión de Contenedores

```bash
# Ver contenedores corriendo
docker ps

# Ver todos los contenedores (incluyendo detenidos)
docker ps -a

# Detener contenedor
docker stop <nombre>

# Iniciar contenedor detenido
docker start <nombre>

# Reiniciar contenedor
docker restart <nombre>

# Eliminar contenedor
docker rm <nombre>

# Eliminar contenedor corriendo (forzar)
docker rm -f <nombre>

# Eliminar todos los contenedores detenidos
docker container prune
```

## Gestión de Imágenes

```bash
# Ver imágenes
docker images

# Eliminar imagen
docker rmi <nombre>

# Eliminar imágenes sin usar
docker image prune

# Construir imagen
docker build -t <nombre> .

# Construir sin cache
docker build --no-cache -t <nombre> .
```

## Logs y Debugging

```bash
# Ver logs
docker logs <nombre>

# Seguir logs en tiempo real
docker logs -f <nombre>

# Ver últimas 50 líneas
docker logs --tail 50 <nombre>

# Ejecutar comando en contenedor
docker exec <nombre> <comando>

# Abrir shell interactiva
docker exec -it <nombre> bash

# Ver estadísticas
docker stats <nombre>

# Ver procesos
docker top <nombre>
```

## Limpieza

```bash
# Eliminar todo lo que no se usa
docker system prune

# Eliminar todo (incluyendo volúmenes)
docker system prune -a --volumes

# Ver espacio usado
docker system df
```

---

# 🐛 Solución de Problemas

## Problema: Puerto ya en uso

**Error**: `Bind for 0.0.0.0:8080 failed: port is already allocated`

**Solución**:
```bash
# Opción 1: Usar otro puerto
docker run -d -p 8081:5000 --name mi-gatitos gatitos-app

# Opción 2: Detener el contenedor que usa el puerto
docker ps
docker stop <contenedor-que-usa-8080>
```

## Problema: Contenedor no inicia

**Solución**:
```bash
# Ver logs para identificar el error
docker logs mi-gatitos

# Ejecutar en modo interactivo para ver errores
docker run -it -p 8080:5000 gatitos-app
```

## Problema: No se ve la página

**Verificar**:
1. ¿El contenedor está corriendo? → `docker ps`
2. ¿El puerto está bien mapeado? → Revisar columna PORTS
3. ¿La URL es correcta? → http://localhost:8080 (no 5000)
4. ¿Hay firewall bloqueando? → Revisar configuración

## Problema: Cambios no se reflejan

**Solución**:
```bash
# Reconstruir la imagen
docker build -t gatitos-app .

# Detener y eliminar contenedor viejo
docker stop mi-gatitos
docker rm mi-gatitos

# Crear nuevo contenedor con la imagen actualizada
docker run -d -p 8080:5000 --name mi-gatitos gatitos-app
```

---

# 📚 Recursos Adicionales

- [Documentación oficial de Docker](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/) - Repositorio de imágenes
- [Cat as a Service API](https://cataas.com/) - API de gatitos usada
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

# ✅ Checklist de Aprendizaje

- [ ] Ejecuté la app localmente
- [ ] Entiendo los problemas de las apps locales
- [ ] Entiendo qué es Docker
- [ ] Leí y entendí el Dockerfile línea por línea
- [ ] Construí una imagen Docker
- [ ] Ejecuté un contenedor
- [ ] Mapeé puertos correctamente
- [ ] Vi los logs de un contenedor
- [ ] Detuve y eliminé contenedores
- [ ] Comparé local vs Docker
- [ ] Ejecuté múltiples contenedores simultáneamente
- [ ] Entiendo cuándo usar Docker

---

# 🎉 ¡Felicidades!

Has completado la práctica de Docker. Ahora sabes:

✅ Qué es Docker y para qué sirve  
✅ Cómo crear un Dockerfile  
✅ Cómo construir imágenes  
✅ Cómo ejecutar contenedores  
✅ Las diferencias entre local y Docker  
✅ Comandos básicos de Docker  

## 🚀 Próximos Pasos

1. **Docker Compose**: Aprende a orquestar múltiples contenedores
2. **Volúmenes**: Persistir datos entre ejecuciones
3. **Redes**: Comunicación entre contenedores
4. **Docker Hub**: Publicar tus imágenes
5. **Producción**: Desplegar apps dockerizadas

---

**💡 Recuerda**: Docker es una herramienta, no una solución mágica. Úsala cuando tenga sentido para tu proyecto.
