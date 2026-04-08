# 🐱 Comandos Docker - Práctica de Gatitos

Todos los comandos Docker que necesitas para trabajar con la app de gatitos.

---

## 🎯 Comandos Básicos de la Práctica

### 1️⃣ Construir la Imagen

```bash
# Construir la imagen de gatitos
docker build -t gatitos-app .

# Construir sin usar cache (si hiciste cambios)
docker build --no-cache -t gatitos-app .

# Construir con un tag específico
docker build -t gatitos-app:v1.0 .
```

### 2️⃣ Ver Imágenes

```bash
# Ver todas las imágenes
docker images

# Buscar solo la imagen de gatitos
docker images | grep gatitos

# Ver detalles de la imagen
docker inspect gatitos-app
```

### 3️⃣ Ejecutar el Contenedor

```bash
# Ejecutar contenedor básico
docker run -d -p 8080:5000 --name mi-gatitos gatitos-app

# Ejecutar en otro puerto
docker run -d -p 9000:5000 --name gatitos-9000 gatitos-app

# Ejecutar en modo interactivo (ver logs directamente)
docker run -p 8080:5000 --name mi-gatitos gatitos-app

# Ejecutar con reinicio automático
docker run -d -p 8080:5000 --name mi-gatitos --restart always gatitos-app
```

**Explicación del comando**:
- `docker run`: Crear y ejecutar contenedor
- `-d`: Modo detached (segundo plano)
- `-p 8080:5000`: Mapear puerto 8080 (tu PC) → 5000 (contenedor)
- `--name mi-gatitos`: Nombre del contenedor
- `gatitos-app`: Imagen a usar

### 4️⃣ Ver Contenedores

```bash
# Ver contenedores corriendo
docker ps

# Ver todos los contenedores (incluyendo detenidos)
docker ps -a

# Ver solo el contenedor de gatitos
docker ps | grep gatitos
```

---

## 📊 Ver Logs

```bash
# Ver todos los logs
docker logs mi-gatitos

# Ver logs en tiempo real (seguir logs)
docker logs -f mi-gatitos

# Ver últimas 20 líneas
docker logs --tail 20 mi-gatitos

# Ver logs con timestamps
docker logs -t mi-gatitos

# Ver últimas 10 líneas y seguir
docker logs --tail 10 -f mi-gatitos

# Ver logs de los últimos 5 minutos
docker logs --since 5m mi-gatitos
```

**Salida esperada**:
```
🐳 Iniciando Gatitos App en Docker...
📍 La app estará disponible en el puerto mapeado
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000
192.168.65.1 - - [03/Nov/2025 23:43:46] "GET / HTTP/1.1" 200 -
```

---

## 🔧 Gestionar el Contenedor

```bash
# Detener el contenedor
docker stop mi-gatitos

# Iniciar el contenedor detenido
docker start mi-gatitos

# Reiniciar el contenedor
docker restart mi-gatitos

# Pausar el contenedor (congela procesos)
docker pause mi-gatitos

# Despausar
docker unpause mi-gatitos

# Ver estado del contenedor
docker inspect -f '{{.State.Status}}' mi-gatitos
```

---

## 📈 Monitoreo y Estadísticas

```bash
# Ver estadísticas en tiempo real
docker stats mi-gatitos

# Ver uso de CPU, memoria, red
docker stats

# Ver procesos corriendo en el contenedor
docker top mi-gatitos

# Ver información completa del contenedor
docker inspect mi-gatitos

# Ver solo la IP del contenedor
docker inspect -f '{{.NetworkSettings.IPAddress}}' mi-gatitos

# Ver puertos mapeados
docker port mi-gatitos
```

---

## 🐚 Ejecutar Comandos Dentro del Contenedor

```bash
# Ver archivos en el contenedor
docker exec mi-gatitos ls -la /app

# Ver el contenido de app.py
docker exec mi-gatitos cat /app/app.py

# Ver procesos
docker exec mi-gatitos ps aux

# Probar endpoint de salud desde dentro
docker exec mi-gatitos curl http://localhost:5000/health

# Abrir una terminal interactiva dentro del contenedor
docker exec -it mi-gatitos bash

# Dentro del bash puedes hacer:
ls -la
cat app.py
pwd
env
exit  # Para salir
```

---

## 📁 Copiar Archivos

```bash
# Copiar app.py DEL contenedor a tu PC
docker cp mi-gatitos:/app/app.py ./app_backup.py

# Copiar templates DEL contenedor
docker cp mi-gatitos:/app/templates ./templates_backup

# Copiar archivo DE tu PC al contenedor
docker cp nuevo_archivo.txt mi-gatitos:/app/

# Copiar y sobrescribir app.py en el contenedor
docker cp app_modificado.py mi-gatitos:/app/app.py
```

---

## 🗑️ Eliminar Contenedor

```bash
# Detener y eliminar el contenedor
docker stop mi-gatitos
docker rm mi-gatitos

# Detener y eliminar en un solo comando
docker stop mi-gatitos && docker rm mi-gatitos

# Eliminar contenedor corriendo (forzar)
docker rm -f mi-gatitos

# Eliminar todos los contenedores detenidos
docker container prune
```

---

## 🧹 Limpieza

```bash
# Eliminar la imagen de gatitos
docker rmi gatitos-app

# Eliminar imagen forzadamente
docker rmi -f gatitos-app

# Eliminar todas las imágenes sin usar
docker image prune -a

# Eliminar todo (contenedores, imágenes, redes, volúmenes)
docker system prune -a --volumes

# Ver espacio usado por Docker
docker system df
```

---

## 🎓 Ejercicios Prácticos

### Ejercicio 1: Ejecutar Múltiples Contenedores

```bash
# Crear 3 contenedores de gatitos
docker run -d -p 8080:5000 --name gatitos-1 gatitos-app
docker run -d -p 8081:5000 --name gatitos-2 gatitos-app
docker run -d -p 8082:5000 --name gatitos-3 gatitos-app

# Ver todos corriendo
docker ps

# Abrir en navegador:
# http://localhost:8080
# http://localhost:8081
# http://localhost:8082

# Detener todos
docker stop gatitos-1 gatitos-2 gatitos-3

# Eliminar todos
docker rm gatitos-1 gatitos-2 gatitos-3
```

### Ejercicio 2: Ver Logs de Todos los Contenedores

```bash
# Ver logs de cada uno
docker logs gatitos-1
docker logs gatitos-2
docker logs gatitos-3

# Ver stats de todos
docker stats gatitos-1 gatitos-2 gatitos-3
```

### Ejercicio 3: Modificar y Reconstruir

```bash
# 1. Modificar app_docker.py (agregar más URLs de gatitos)

# 2. Detener y eliminar contenedor viejo
docker stop mi-gatitos
docker rm mi-gatitos

# 3. Reconstruir la imagen
docker build -t gatitos-app:v2 .

# 4. Ejecutar con la nueva versión
docker run -d -p 8080:5000 --name mi-gatitos gatitos-app:v2

# 5. Verificar cambios
docker logs mi-gatitos
```

### Ejercicio 4: Comparar Local vs Docker

```bash
# Terminal 1: App local
uv run python app.py
# Abre: http://127.0.0.1:5000

# Terminal 2: App Docker
docker run -d -p 8080:5000 --name mi-gatitos gatitos-app
# Abre: http://localhost:8080

# Compara:
# - Badge: Verde (local) vs Azul (Docker)
# - Fondo: Morado (local) vs Azul (Docker)
# - Puerto: 5000 (local) vs 8080 (Docker)
```

---

## 🌐 Probar la App

```bash
# Abrir en navegador
open http://localhost:8080

# Probar endpoint de salud con curl
curl http://localhost:8080/health

# Probar desde dentro del contenedor
docker exec mi-gatitos curl http://localhost:5000/health

# Ver requests en los logs
docker logs -f mi-gatitos
# Luego abre el navegador y verás las peticiones
```

---

## 🐛 Solución de Problemas

### Problema: Puerto ya en uso

```bash
# Error: Bind for 0.0.0.0:8080 failed: port is already allocated

# Solución 1: Usar otro puerto
docker run -d -p 8081:5000 --name mi-gatitos gatitos-app

# Solución 2: Detener contenedor que usa el puerto
docker ps
docker stop <contenedor-que-usa-8080>
```

### Problema: Contenedor no inicia

```bash
# Ver logs para identificar el error
docker logs mi-gatitos

# Ejecutar en modo interactivo para ver errores
docker run -it -p 8080:5000 gatitos-app
```

### Problema: No se ven los cambios

```bash
# Reconstruir la imagen sin cache
docker build --no-cache -t gatitos-app .

# Detener y eliminar contenedor viejo
docker rm -f mi-gatitos

# Crear nuevo contenedor
docker run -d -p 8080:5000 --name mi-gatitos gatitos-app
```

### Problema: Error "No such container"

```bash
# ❌ Error
docker logs gatitos-app
# Error: No such container: gatitos-app

# ✅ Correcto - Usar el nombre del CONTENEDOR, no de la IMAGEN
docker logs mi-gatitos

# Recordar:
# - gatitos-app = IMAGEN (plantilla)
# - mi-gatitos = CONTENEDOR (instancia corriendo)
```

---

## 📋 Comandos de Referencia Rápida

### Flujo Completo

```bash
# 1. Construir imagen
docker build -t gatitos-app .

# 2. Ejecutar contenedor
docker run -d -p 8080:5000 --name mi-gatitos gatitos-app

# 3. Ver logs
docker logs -f mi-gatitos

# 4. Abrir en navegador
open http://localhost:8080

# 5. Ver estadísticas
docker stats mi-gatitos

# 6. Detener
docker stop mi-gatitos

# 7. Eliminar
docker rm mi-gatitos
```

### Comandos Más Usados

```bash
# Ver contenedores corriendo
docker ps

# Ver logs en tiempo real
docker logs -f mi-gatitos

# Ver estadísticas
docker stats mi-gatitos

# Entrar al contenedor
docker exec -it mi-gatitos bash

# Detener contenedor
docker stop mi-gatitos

# Eliminar contenedor
docker rm mi-gatitos

# Ver imágenes
docker images

# Eliminar imagen
docker rmi gatitos-app
```

---

## 🎯 Diferencias Clave

### Imagen vs Contenedor

```bash
# IMAGEN (gatitos-app)
# - Es la plantilla/receta
# - Se crea con: docker build
# - Se ve con: docker images
# - Se elimina con: docker rmi

# CONTENEDOR (mi-gatitos)
# - Es la instancia corriendo
# - Se crea con: docker run
# - Se ve con: docker ps
# - Se elimina con: docker rm
```

### Puerto Local vs Puerto Docker

```bash
# -p 8080:5000
#    ↑    ↑
#    │    └─ Puerto DENTRO del contenedor (Flask)
#    └─ Puerto en TU PC (navegador)

# Accedes en: http://localhost:8080
# Flask corre en: 5000 (dentro del contenedor)
```

---

## 💡 Tips y Trucos

### Ver solo IDs de contenedores

```bash
docker ps -q
```

### Detener todos los contenedores

```bash
docker stop $(docker ps -q)
```

### Eliminar todos los contenedores detenidos

```bash
docker container prune
```

### Ver tamaño de las imágenes

```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### Ejecutar comando y eliminar contenedor automáticamente

```bash
docker run --rm -p 8080:5000 gatitos-app
```

### Ver logs de múltiples contenedores

```bash
# En terminales separadas
docker logs -f gatitos-1
docker logs -f gatitos-2
```

---

## 📚 Recursos Adicionales

- [Documentación oficial de Docker](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [README principal](./README.md) - Guía completa de la práctica

---

## ✅ Checklist de Comandos

- [ ] `docker build` - Construir imagen
- [ ] `docker images` - Ver imágenes
- [ ] `docker run` - Ejecutar contenedor
- [ ] `docker ps` - Ver contenedores
- [ ] `docker logs` - Ver logs
- [ ] `docker exec` - Ejecutar comandos en contenedor
- [ ] `docker stats` - Ver estadísticas
- [ ] `docker stop` - Detener contenedor
- [ ] `docker start` - Iniciar contenedor
- [ ] `docker rm` - Eliminar contenedor
- [ ] `docker rmi` - Eliminar imagen
- [ ] `docker inspect` - Ver detalles
- [ ] `docker cp` - Copiar archivos

---

**🎉 ¡Con estos comandos dominas Docker para la práctica de gatitos!**

*Recuerda: La práctica hace al maestro. Prueba cada comando y experimenta.* 🐱🐳
