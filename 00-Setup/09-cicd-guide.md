# CI/CD: Integracion y Entrega Continua

## Que es CI/CD?

**CI (Continuous Integration)** y **CD (Continuous Delivery/Deployment)** son practicas
que automatizan la verificacion y entrega de codigo.

```
Desarrollador hace push
        |
        v
  [CI] Se ejecutan automaticamente:
        - Lint (ruff check)
        - Formateo (ruff format --check)
        - Tests (pytest)
        |
    Pasan? ----NO----> Se bloquea el merge, hay que corregir
        |
       SI
        |
        v
  [CD] Opcionalmente:
        - Deploy automatico
        - Publicar paquete
        - Actualizar documentacion
```

**En palabras simples**: cada vez que subes codigo, un servidor lo revisa automaticamente.
Si algo esta mal, te avisa antes de que el codigo llegue a `main`.

## Para que sirve en MLOps?

| Problema | Como lo resuelve CI/CD |
|----------|----------------------|
| "Funciona en mi maquina" | Se ejecuta en un ambiente limpio (Ubuntu en la nube) |
| "Alguien rompio el formato" | Ruff verifica automaticamente |
| "Los tests no pasan" | Se ejecutan en cada push y PR |
| "Se subio codigo sin revisar" | El PR se bloquea si CI falla |

## GitHub Actions: como funciona

GitHub Actions es el sistema de CI/CD integrado en GitHub. Funciona asi:

1. **Defines un workflow** en `.github/workflows/ci.yml`
2. **Un evento lo dispara** (push, pull request, schedule, manual)
3. **GitHub ejecuta los pasos** en una maquina virtual limpia
4. **Ves el resultado** directamente en el PR o en la pestana "Actions"

### Anatomia del archivo ci.yml

```yaml
name: CI                          # Nombre del workflow

on:                               # Cuando se ejecuta
  push:
    branches: [main]              #   - Push a main
  pull_request:
    branches: [main]              #   - PR hacia main

jobs:
  lint-and-test:                  # Nombre del job
    runs-on: ubuntu-latest        # Maquina virtual donde corre

    steps:
      - uses: actions/checkout@v4          # 1. Descarga tu codigo
      - uses: actions/setup-python@v5      # 2. Instala Python
      - uses: astral-sh/setup-uv@v4       # 3. Instala uv (con cache)
      - run: uv sync                       # 4. Instala dependencias
      - run: uv run ruff check .           # 5. Lint
      - run: uv run ruff format --check .  # 6. Formateo
      - run: uv run pytest -q              # 7. Tests
```

### Donde ver los resultados

- En cada PR aparece un check verde o rojo
- En la pestana **Actions** del repositorio ves el historial completo
- Cada step muestra su output (util para debuggear)

## Como se integra a este proyecto

El archivo `.github/workflows/ci.yml` de este repositorio ejecuta:

1. **Checkout**: Descarga el codigo del commit/PR
2. **Setup Python 3.11**: Instala la version que usa el curso
3. **Setup uv**: Instala el gestor de paquetes con cache habilitado
4. **Install dependencies**: `uv sync` instala todo desde el lockfile
5. **Lint**: `ruff check .` busca errores de estilo y bugs
6. **Format check**: `ruff format --check .` verifica formateo consistente
7. **Tests**: `pytest` ejecuta los tests (cuando los haya)

## Conceptos clave

| Concepto | Definicion |
|----------|-----------|
| **Workflow** | Un proceso automatizado definido en YAML |
| **Job** | Una unidad de trabajo dentro del workflow (corre en una VM) |
| **Step** | Un comando individual dentro de un job |
| **Action** | Un paso reutilizable creado por la comunidad (ej: `actions/checkout`) |
| **Runner** | La maquina virtual que ejecuta el job (`ubuntu-latest`) |
| **Artifact** | Archivo generado durante el workflow que puedes descargar |

## Buenas practicas

- Mantener el CI **rapido** (< 5 minutos). Si es lento, nadie lo espera.
- Usar **cache** para dependencias (ya configurado con `setup-uv`).
- Los checks deben **bloquear el merge** si fallan (configurar en GitHub > Settings > Branches).
- Empezar simple: lint + tests. Agregar complejidad solo cuando se necesite.
