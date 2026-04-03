# Git LFS: Large File Storage

> Referencia oficial: <https://git-lfs.com/>

## Que problema soluciona?

Git fue disenado para texto (codigo fuente). Cuando agregas archivos binarios grandes
(imagenes, modelos .bin, datasets .parquet), Git guarda **una copia completa de cada
version** en el historial. Esto causa:

- El repositorio crece de forma incontrolable (un .bin de 50MB x 10 versiones = 500MB de historial)
- `git clone` se vuelve lento
- `git push/pull` consume mucho ancho de banda
- GitHub tiene un limite de 100MB por archivo

**Git LFS resuelve esto** reemplazando los archivos grandes por un **puntero liviano** (< 1KB)
y almacenando el contenido real en un servidor aparte.

```
Sin LFS:
  .git/ contiene TODAS las versiones del archivo grande (500MB+)

Con LFS:
  .git/ contiene solo punteros (~100 bytes cada uno)
  LFS server contiene las versiones reales (descarga bajo demanda)
```

## Cuando usarlo

| Usar LFS | NO usar LFS |
|----------|-------------|
| Imagenes (PNG, JPG, SVG) | Archivos de texto (codigo, markdown, YAML) |
| Modelos serializados (.bin, .pkl, .pt, .onnx) | Archivos pequenos (< 1MB) |
| Datasets grandes (.parquet, .csv > 10MB) | Archivos que cambian frecuentemente como texto |
| Archivos binarios que versionas | Archivos que no necesitas versionar (usar .gitignore) |

**Regla simple**: si el archivo es binario y pesa mas de ~1MB, probablemente deberia estar en LFS.

## Cuando NO usarlo

- **Archivos que cambian en cada commit**: LFS almacena cada version. Si un archivo grande
  cambia constantemente, el storage de LFS crece igual de rapido.
- **Archivos que no necesitas en el repo**: Mejor usar `.gitignore` y descargarlos aparte
  (por ejemplo, datasets de entrenamiento que se descargan via script).
- **Proyectos con muchos colaboradores sin LFS instalado**: Si alguien clona sin LFS,
  obtiene los punteros en vez del contenido real.

## Tutorial practico

### 1. Instalar Git LFS

```bash
# macOS
brew install git-lfs

# Windows
winget install GitHub.GitLFS

# Ubuntu/Debian
sudo apt install git-lfs
```

### 2. Activar en tu repositorio

```bash
# Ejecutar una sola vez (configura los hooks de Git)
git lfs install
```

### 3. Trackear archivos por extension

```bash
# Trackear todas las imagenes PNG
git lfs track "*.png"

# Trackear modelos serializados
git lfs track "*.bin"
git lfs track "*.pkl"

# Trackear archivos grandes en una carpeta especifica
git lfs track "data/raw/**"
```

Esto crea o modifica un archivo `.gitattributes`:

```
*.png filter=lfs diff=lfs merge=lfs -text
*.bin filter=lfs diff=lfs merge=lfs -text
```

### 4. Agregar y commitear normalmente

```bash
# IMPORTANTE: commitear .gitattributes primero
git add .gitattributes
git commit -m "chore: configure Git LFS for images and models"

# Ahora agregar los archivos grandes
git add model.bin
git commit -m "feat: add trained model"
git push
```

### 5. Verificar que funciona

```bash
# Ver que archivos estan trackeados por LFS
git lfs ls-files

# Ver las reglas de tracking
git lfs track

# Ver el uso de almacenamiento
git lfs env
```

## Como se usa en este repositorio

Este proyecto trackea imagenes PNG con LFS (ver `.gitattributes` en la raiz):

```
*.png filter=lfs diff=lfs merge=lfs -text
```

Esto significa que cualquier `.png` que agregues sera manejado automaticamente por LFS.

## Preguntas frecuentes

**Que pasa si clono sin tener LFS instalado?**
Obtienes archivos de puntero (texto plano, ~130 bytes) en vez del contenido real.
Solucion: `git lfs install && git lfs pull`.

**GitHub cobra por LFS?**
GitHub da 1GB gratis de storage y 1GB/mes de bandwidth.
Para proyectos academicos es suficiente. Ver: <https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-storage-and-bandwidth-usage>

**Puedo dejar de trackear un archivo con LFS?**
Si: `git lfs untrack "*.png"`, pero las versiones ya almacenadas siguen en LFS.
