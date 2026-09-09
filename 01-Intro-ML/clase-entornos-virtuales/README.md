# Gestión de dependencias en Python con `uv`

> **¿Por qué aprender `uv`?** En un flujo de trabajo MLOps, la reproducibilidad de entornos no es opcional — es un requisito. `uv` resuelve de raíz los problemas clásicos de "funciona en mi máquina" y los pipelines de CI/CD lentos, consolidando en una sola herramienta lo que antes requería `pip`, `venv`, `pip-tools`, `pipx` y `pyenv`.

---

## 1. ¿Qué es `uv`?

`uv` es un gestor de paquetes y proyectos Python de nueva generación, **escrito en Rust** por el equipo de Astral (los mismos que crearon el linter `ruff`). Fue lanzado a principios de 2024 y ya se considera estable para producción.

Su ventaja central es la **velocidad**: usa el algoritmo de resolución de dependencias **PubGrub** (el mismo de Cargo/Dart) y ejecuta instalaciones en paralelo desde un binario compilado, sin depender del intérprete de Python para sus operaciones internas. En la práctica, esto se traduce en instalaciones **10x a 100x más rápidas** que `pip`.

```
┌─────────────────────────────────────────────────────────┐
│  uv reemplaza en una sola herramienta:                  │
│                                                         │
│  pip  +  venv  +  pip-tools  +  pyenv  +  pipx         │
└─────────────────────────────────────────────────────────┘
```

### Cache global inteligente

`uv` mantiene un cache global en `~/.cache/uv`. Si dos proyectos usan la misma versión de un paquete, este se descarga **una sola vez**. Esto es especialmente útil en CI/CD donde múltiples jobs instalan conjuntos similares de dependencias.

---

## 2. Instalación

```bash
# Opción 1: pip (si ya tienes Python ≥ 3.8)
pip install uv

# Opción 2: instalador oficial (no requiere Python previo)
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
irm https://astral.sh/uv/install.ps1 | iex         # Windows (PowerShell)

# Opción 3: Homebrew (macOS — la vieja confiable)
brew install uv

# Verificar instalación
uv --version

# Actualizar uv a la última versión
uv self update
```

> **Nota para MLOps:** En Dockerfiles y pipelines de CI, la opción del instalador oficial es ideal porque no depende de que Python ya esté disponible en la imagen base. `uv` puede incluso bootstrapear el intérprete de Python por ti.

---

## 3. Gestión de versiones de Python

Una de las capacidades más poderosas de `uv` es manejar múltiples versiones de Python sin herramientas externas.

```bash
# Instalar una o varias versiones de Python
uv python install 3.11.5
uv python install 3.11.5 3.10.14 3.9.19   # varias a la vez

# Listar todas las versiones que uv conoce (instaladas y disponibles)
uv python list

# Fijar la versión de Python para el proyecto actual
# Esto escribe un archivo .python-version en el directorio
uv python pin 3.11

# Verificar la versión activa en el contexto del proyecto
python --version   # uv lee .python-version automáticamente
```

**Caso de uso en monorepos:** Puedes tener múltiples proyectos en un mismo repositorio, cada uno con su propio `.python-version`. `uv` entiende el contexto de cada directorio y usa la versión correcta para cada uno, sin conflictos.

---

## 4. Inicializar un proyecto

```bash
# Crear un nuevo proyecto
uv init mi-proyecto

# Crear el proyecto con una versión específica de Python
uv init mi-proyecto --python 3.11

# Si ya estás en el directorio del proyecto
uv init
uv init --python 3.11
```

Esto genera la siguiente estructura:

```
mi-proyecto/
├── .python-version      ← versión de Python fijada
├── .venv/               ← entorno virtual (creado automáticamente)
├── pyproject.toml       ← configuración del proyecto (PEP 621)
├── uv.lock              ← lockfile con versiones y hashes exactos
└── main.py
```

### Truco avanzado: cambiar la versión de Python en un proyecto existente

Si necesitas migrar la versión de Python de un proyecto, puedes editarlo directamente en `pyproject.toml`:

```toml
[project]
requires-python = ">=3.11"
```

Luego ejecuta:

```bash
uv sync   # uv detecta el cambio y reconstruye el entorno
```

---

## 5. El archivo `pyproject.toml` y el `uv.lock`

`uv` trabaja con dos archivos que juntos garantizan la reproducibilidad:

| Archivo | Propósito | ¿Se hace commit? |
|---|---|---|
| `pyproject.toml` | Dependencias declaradas con rangos de versión | Sí |
| `uv.lock` | Versiones y hashes exactos de cada paquete | Sí |

El `uv.lock` es **universal**: funciona en Windows, macOS y Linux desde el mismo archivo, a diferencia de un `requirements.txt` generado con `pip freeze` que es específico de la plataforma.

---

## 6. Instalar dependencias: tres comandos, tres propósitos

### `uv add` — dependencias permanentes del proyecto

```bash
# Agregar una dependencia
uv add requests pandas scikit-learn

# Agregar con versión específica
uv add "pandas>=2.0,<3.0"

# Agregar dependencia de desarrollo (no se incluye en producción)
uv add ruff pytest --group dev

# Agregar dependencia opcional
uv add "boto3" --optional aws
```

`uv add` hace tres cosas automáticamente:
1. Actualiza `[project.dependencies]` en `pyproject.toml`
2. Actualiza `uv.lock` con versiones y hashes exactos
3. Instala el paquete en el entorno `.venv`

### `uv pip install` — instalación temporal

```bash
# Instalar en el entorno activo SIN modificar pyproject.toml
uv pip install jupyter

# Útil para: exploración rápida, notebooks de análisis ad-hoc
# NO usar para dependencias del proyecto productivo
```

### `uv sync` — sincronizar el entorno con el lockfile

```bash
# Sincronizar entorno con uv.lock (el estándar para CI/CD)
uv sync

# Incluir grupos de dependencias adicionales
uv sync --all-groups

# Incluir un grupo específico
uv sync --group dev
```

> **Regla de oro para MLOps:** En pipelines de CI/CD, siempre usa `uv sync` en lugar de `uv add`. El `uv.lock` ya tiene todo lo necesario; `uv sync` simplemente reconstruye el entorno de forma determinística.

---

## 7. `uv run` — ejecutar sin activar el entorno

Este es el comando que la profe más recomienda para quienes están empezando, porque elimina el error más común: olvidar activar el entorno virtual.

```bash
# Ejecutar un script
uv run python main.py

# Ejecutar con dependencias del grupo de desarrollo
uv run --with dev python main.py

# Ejecutar una herramienta directamente
uv run ruff check src/
uv run pytest tests/
```

**¿Por qué importa en MLOps?** En scripts de entrenamiento, pipelines de datos y tareas programadas (cron, Airflow, etc.), el entorno nunca está "activado". `uv run` garantiza que siempre se use el entorno correcto, independientemente del contexto de ejecución.

### Activación manual (cuando sí es necesaria)

```bash
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

---

## 8. Gestión avanzada de dependencias

### Eliminar y actualizar paquetes

```bash
# Eliminar una dependencia
uv remove requests

# Actualizar una dependencia específica
uv update pandas

# IMPORTANTE: precaución con uv update
# Antes de actualizar, siempre:
# 1. Lee las notas de la nueva versión (changelog, breaking changes)
# 2. Verifica compatibilidad con Semantic Versioning (MAJOR.MINOR.PATCH)
#    - PATCH (1.0.0 → 1.0.1): corrección de bugs, generalmente seguro
#    - MINOR (1.0.0 → 1.1.0): nuevas funciones, puede haber cambios
#    - MAJOR (1.0.0 → 2.0.0): cambios que rompen compatibilidad, CUIDADO
# 3. Ejecuta la suite de tests después de actualizar
# 4. Notifica al equipo los cambios
```

### Regenerar el lockfile explícitamente

```bash
# Volver a resolver todas las dependencias y escribir uv.lock desde cero
uv lock

# Útil cuando: cambias pyproject.toml manualmente, 
# hay conflictos de resolución, o quieres asegurar reproducibilidad
```

### Scripts con metadatos de dependencias (PEP 723)

`uv` soporta scripts Python con dependencias declaradas directamente en el archivo:

```bash
# Agregar metadatos de dependencias al script
uv add --script analisis.py pandas matplotlib

# El script ahora tiene un bloque como este al inicio:
# # /// script
# # requires-python = ">=3.11"
# # dependencies = ["pandas", "matplotlib"]
# # ///

# Ejecutar el script: uv instala las dependencias automáticamente
uv run analisis.py
```

Esto es ideal para scripts de análisis que comparten compañeros de equipo sin necesidad de un proyecto completo.

---

## 9. Grupos de dependencias

Los grupos permiten separar dependencias según su propósito:

```bash
# Agregar al grupo de desarrollo
uv add ruff pytest black mypy --group dev

# Agregar al grupo de documentación
uv add mkdocs mkdocstrings --group docs

# Sincronizar solo producción (sin dev)
uv sync

# Sincronizar todos los grupos
uv sync --all-groups

# Ejecutar con el grupo dev activo
uv run --with dev pytest tests/
```

**Estructura resultante en `pyproject.toml`:**

```toml
[project]
name = "mi-modelo"
dependencies = [
    "scikit-learn>=1.3",
    "pandas>=2.0",
    "mlflow>=2.10",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
    "mypy>=1.8",
]
docs = [
    "mkdocs>=1.5",
]
```

---

## 10. Herramientas globales con `uv tool`

```bash
# Instalar una herramienta CLI globalmente (como pipx, pero más rápido)
uv tool install ruff

# Usar la herramienta
ruff check src/

# Alternativa: ejecutar sin instalar globalmente
uv run ruff check src/
uv tool run ruff check src/   # equivalente
```

Herramientas útiles en MLOps para instalar con `uv tool`:

```bash
uv tool install ruff           # linter y formatter
uv tool install mypy           # type checking
uv tool install pre-commit     # hooks de git
```

---

## 11. Integración con CI/CD

El flujo recomendado para GitHub Actions:

```yaml
# .github/workflows/train.yml
name: Train Model

on: [push]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true   # cache del uv.lock entre runs

      - name: Set up Python
        run: uv python install

      - name: Install dependencies
        run: uv sync --all-groups

      - name: Run tests
        run: uv run pytest tests/

      - name: Train model
        run: uv run python scripts/train.py
```

**Ventajas para MLOps:**
- `enable-cache: true` evita re-descargar paquetes en cada run
- `uv sync` garantiza exactamente las mismas versiones del `uv.lock`
- Tiempos de instalación significativamente menores (crítico en pipelines de entrenamiento frecuentes)

---

## 12. Reconstruir el entorno desde cero

```bash
# Eliminar el entorno virtual
rm -rf .venv

# Reconstruir exactamente como lo define el lockfile
uv sync

# Esto garantiza que el entorno local es idéntico al de CI/CD
```

---

## 13. Flujo de trabajo completo recomendado

```bash
# 1. Crear el proyecto
uv init mi-modelo-ml --python 3.11

# 2. Agregar dependencias de producción
uv add scikit-learn pandas mlflow

# 3. Agregar dependencias de desarrollo
uv add pytest ruff mypy --group dev

# 4. Desarrollar y ejecutar
uv run python src/train.py

# 5. Correr tests
uv run pytest tests/

# 6. Hacer commit del pyproject.toml y uv.lock
git add pyproject.toml uv.lock
git commit -m "chore: add initial dependencies"

# 7. En una máquina nueva o en CI, reproducir el entorno exacto
uv sync
```

---

## 14. Actividad de clase: arma tu primer proyecto reproducible

Esta es la práctica central de la clase de entornos virtuales. Van a recorrer, con sus propias manos, el ciclo completo que acaban de ver en la teoría: crear un repositorio, iniciar un proyecto con una versión de Python específica, agregar una dependencia real, exponer un comando propio como alias, y comprobar que todo el entorno se puede reconstruir desde cero con un solo comando.

**Formato:** equipos de 2-3 personas, en salas de Zoom.
**Duración sugerida:** 25 minutos.

### Paso 1 — Crear el repositorio

```bash
mkdir saludo-equipo
cd saludo-equipo
git init
```

### Paso 2 — Iniciar el proyecto con una versión de Python específica

Usen `--package` para que `uv` genere una estructura instalable (la necesitamos para el alias del paso 4). Elijan una versión de Python distinta a la que usa el resto del curso (por ejemplo 3.12), para practicar que cada proyecto fija la suya sin depender de nada externo.

```bash
uv init --package . --python 3.12
```

Esto crea `pyproject.toml`, `.python-version`, y el código fuente en `src/saludo_equipo/__init__.py`.

> **Nota:** si están practicando dentro de una carpeta que vive adentro de otro repositorio con su propio `pyproject.toml` (como pasa en este curso), verifiquen que su carpeta **no** haya quedado listada en `[tool.uv.workspace] members` de ese `pyproject.toml` de más arriba. Si queda ahí, `uv` va a intentar compartir un solo entorno entre los dos proyectos, y si las versiones de Python no coinciden, van a ver un error de "incompatible with the project's Python requirement" — un caso real que le pasó a la profe armando este mismo curso.

### Paso 3 — Agregar una dependencia real

```bash
uv add rich
```

Revisen `pyproject.toml`: la dependencia quedó registrada ahí, y también en `uv.lock`.

### Paso 4 — Escribir el script y exponerlo como alias

Abran `src/saludo_equipo/__init__.py` y reemplacen su contenido. Usen `logging`, no `print` — es el estándar del curso.

```python
import logging

from rich.console import Console

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
console = Console()


def main() -> None:
    logger.info("Entorno reconstruido correctamente.")
    console.print("[bold green]Hola desde el equipo, armado con uv[/bold green]")
```

`uv init --package` ya dejó configurado el alias en `pyproject.toml`:

```toml
[project.scripts]
saludo-equipo = "saludo_equipo:main"
```

Sincronicen y corran el alias — sin activar el entorno a mano:

```bash
uv sync
uv run saludo-equipo
```

### Paso 5 — Reconstruir el entorno desde cero

La prueba real de reproducibilidad: borren el entorno y reconstrúyanlo solo a partir del lockfile.

```bash
rm -rf .venv
uv sync
uv run saludo-equipo
```

Si el alias vuelve a funcionar igual, el entorno es reproducible.

### Paso 6 — Commit

```bash
git add pyproject.toml uv.lock src/
git commit -m "feat: primer proyecto con uv"
```

**Entregable:** capturen pantalla del `uv run saludo-equipo` después de reconstruir el entorno (paso 5) y compártanla en la plenaria.

### Reto extra, si sobra tiempo

Agreguen un segundo alias al mismo proyecto (otra entrada en `[project.scripts]`, apuntando a otra función), y ejecútenlo con `uv run`. Un solo proyecto puede exponer varios comandos.

---

## Resumen de comandos clave

| Comando | ¿Qué hace? | ¿Modifica pyproject.toml? |
|---|---|---|
| `uv init` | Crea un nuevo proyecto | Si Lo crea |
| `uv add <pkg>` | Agrega dependencia permanente | Sí |
| `uv remove <pkg>` | Elimina dependencia | Sí |
| `uv pip install <pkg>` | Instala sin registrar | No |
| `uv sync` | Sincroniza entorno con lockfile | No |
| `uv run <cmd>` | Ejecuta en el entorno del proyecto | No |
| `uv lock` | Regenera el lockfile | No |
| `uv update <pkg>` | Actualiza dependencia | Sí |
| `uv python install X` | Instala versión de Python | No |
| `uv python pin X` | Fija versión en `.python-version` | No* |
| `uv tool install <tool>` | Instala herramienta global | No |

*Escribe `.python-version`, no `pyproject.toml`

---

## Lectura adicional

- [Documentación oficial de uv](https://docs.astral.sh/uv/)
- [Guía completa y avanzada — Deepnote](https://deepnote.com/blog/ultimate-guide-to-uv-library-in-python)
- [Repositorio oficial en GitHub](https://github.com/astral-sh/uv)
- [PEP 723 — Scripts con metadatos de dependencias](https://peps.python.org/pep-0723/)