# Guía Básica de Docker

Esta guía proporciona una introducción a Docker y los comandos más útiles para trabajar con contenedores.

## ¿Qué es Docker?

Docker es una plataforma que permite desarrollar, enviar y ejecutar aplicaciones en contenedores. Los contenedores son unidades estandarizadas de software que empaquetan el código y todas sus dependencias para que la aplicación se ejecute de manera rápida y confiable en diferentes entornos.

## Conceptos Básicos

- **Imagen**: Plantilla de solo lectura con instrucciones para crear un contenedor Docker.
- **Contenedor**: Instancia ejecutable de una imagen.
- **Dockerfile**: Archivo de texto con instrucciones para construir una imagen.
- **Registro**: Repositorio de imágenes Docker (como Docker Hub).
- **Volumen**: Mecanismo para persistir datos generados y utilizados por contenedores.

## Comandos Esenciales de Docker

### Gestión de Imágenes

```bash
# Listar imágenes disponibles localmente
docker images

# Buscar imágenes en Docker Hub
docker search ubuntu

# Descargar una imagen
docker pull python:3.11-slim

# Construir una imagen desde un Dockerfile
docker build -t mi-app:1.0 .

# Eliminar una imagen
docker rmi mi-app:1.0
```

### Gestión de Contenedores

```bash
# Crear y ejecutar un contenedor
docker run -d -p 8080:80 --name mi-contenedor nginx

# Listar contenedores en ejecución
docker ps

# Listar todos los contenedores (incluyendo los detenidos)
docker ps -a

# Detener un contenedor
docker stop mi-contenedor

# Iniciar un contenedor detenido
docker start mi-contenedor

# Eliminar un contenedor
docker rm mi-contenedor

# Eliminar todos los contenedores detenidos
docker container prune
```

### Logs y Monitoreo

```bash
# Ver logs de un contenedor
docker logs mi-contenedor

# Ver logs en tiempo real
docker logs -f mi-contenedor

# Ver estadísticas de uso de recursos
docker stats

# Ver procesos en ejecución dentro de un contenedor
docker top mi-contenedor
```

### Interacción con Contenedores

```bash
# Ejecutar un comando en un contenedor en ejecución
docker exec -it mi-contenedor bash

# Copiar archivos desde/hacia un contenedor
docker cp archivo.txt mi-contenedor:/ruta/destino/
docker cp mi-contenedor:/ruta/origen/archivo.txt ./

# Ver información detallada de un contenedor
docker inspect mi-contenedor
```

### Redes

```bash
# Listar redes
docker network ls

# Crear una red
docker network create mi-red

# Conectar un contenedor a una red
docker network connect mi-red mi-contenedor

# Inspeccionar una red
docker network inspect mi-red
```

### Volúmenes

```bash
# Listar volúmenes
docker volume ls

# Crear un volumen
docker volume create mi-volumen

# Ejecutar un contenedor con un volumen
docker run -v mi-volumen:/data mi-app

# Eliminar un volumen
docker volume rm mi-volumen
```

## Ejemplos Prácticos

### Ejecutar un servidor web Nginx

```bash
docker run -d -p 8080:80 --name mi-nginx nginx
# Accede a http://localhost:8080 en tu navegador
```

### Ejecutar una base de datos PostgreSQL

```bash
docker run -d \
  --name mi-postgres \
  -e POSTGRES_PASSWORD=secreto \
  -e POSTGRES_USER=usuario \
  -e POSTGRES_DB=midb \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:14
```

### Ejecutar una aplicación con Docker Compose

Archivo `docker-compose.yml`:
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: secreto
```

Comandos:
```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down
```

## Buenas Prácticas

1. **Imágenes ligeras**: Usa imágenes base pequeñas como Alpine o slim.
2. **Un proceso por contenedor**: Cada contenedor debe ejecutar un solo proceso.
3. **Datos efímeros**: Los contenedores no deben almacenar datos persistentes.
4. **Variables de entorno**: Configura tus aplicaciones con variables de entorno.
5. **Etiquetas específicas**: Usa etiquetas específicas en lugar de `latest`.
6. **Optimiza capas**: Minimiza el número de capas en tu Dockerfile.
7. **Seguridad**: No ejecutes contenedores como root cuando sea posible.

## Solución de Problemas Comunes

### El contenedor se detiene inmediatamente

Verifica que el proceso principal no esté terminando:
```bash
docker logs mi-contenedor
```

### Problemas de red

Verifica la configuración de red:
```bash
docker network inspect bridge
```

### Problemas de espacio en disco

Limpia recursos no utilizados:
```bash
docker system prune -a
```

### Contenedor no accesible

Verifica el mapeo de puertos:
```bash
docker port mi-contenedor
```

## Recursos Adicionales

- [Documentación oficial de Docker](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/) - Registro público de imágenes
- [Play with Docker](https://labs.play-with-docker.com/) - Entorno de pruebas online
