## Python y Entornos Virtuales (uv, venv, Poetry)

### 1) Instalar Python 3.11+ (recomendado 3.11)

- macOS (recomendado: pyenv):

```bash
brew update
brew install pyenv

# Configura tu shell (zsh)
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
exec "$SHELL"

# Instala y selecciona una versión de Python
pyenv install 3.11.9
pyenv global 3.11.9           # versión por defecto a nivel de usuario

# Dentro del repositorio del curso (local a la carpeta)
pyenv local 3.11.9
python -V
```

- Windows (PowerShell como Administrador):

```powershell
# Instalar pyenv-win (método oficial)
Invoke-WebRequest -UseBasicParsing `
  -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" `
  -OutFile "./install-pyenv-win.ps1"; & "./install-pyenv-win.ps1"

# Si aparece error UnauthorizedAccess, ejecuta primero:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine

# Cierra y abre la terminal, luego:
pyenv install 3.11.9
pyenv global 3.11.9
# Dentro del repositorio del curso
pyenv local 3.11.9
python -V
```

Verificar (ambos sistemas):

```bash
python -V
# Esperado: Python 3.11.9
```

---

### 2) ¿Qué es un entorno virtual y por qué lo necesitas?

Un **entorno virtual** es una carpeta aislada que contiene su propia copia de
Python y de las dependencias (librerías) que instales. Esto evita conflictos
entre proyectos que necesiten versiones distintas de una misma librería.

#### Comparación rápida de herramientas

| Herramienta | ¿Qué es? | Ventajas | Desventajas |
|---|---|---|---|
| **venv** | Módulo incluido en Python (stdlib) | No requiere instalar nada extra; estándar oficial | Lento para resolver dependencias; no gestiona versiones de Python |
| **uv** | Gestor de paquetes y proyectos ultrarrápido escrito en Rust (por Astral) | 10-100× más rápido que pip; reemplaza pip + venv + pyenv + poetry en una sola herramienta | Proyecto relativamente nuevo (2024); ecosistema aún en crecimiento |
| **Miniconda / Conda** | Gestor de entornos y paquetes multilenguaje (Python, R, C…) | Ideal para ciencia de datos; maneja dependencias nativas (CUDA, MKL); puede instalar Python por sí solo | Más pesado; los entornos ocupan más espacio; resolver dependencias puede ser lento |
| **Poetry** | Gestor de dependencias y empaquetado de Python | Lockfile determinista; publicación a PyPI integrada | Más lento que uv; curva de aprendizaje moderada |

> **En este curso usamos uv** por su velocidad y simplicidad, pero conocer las
> alternativas te permitirá elegir la herramienta adecuada según el proyecto.

---

### 3) uv — gestor de paquetes recomendado

[uv](https://docs.astral.sh/uv/) es un gestor de paquetes y proyectos Python
extremadamente rápido, escrito en Rust por [Astral](https://astral.sh) (los
creadores de Ruff). Puede reemplazar a `pip`, `pip-tools`, `pipx`, `poetry`,
`pyenv` y `virtualenv` en una sola herramienta.

#### Instalar uv

- macOS/Linux:

```bash
# Opción 1: Homebrew
brew install uv

# Opción 2: instalador oficial
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Crear y activar un entorno virtual

```bash
uv venv                        # crea .venv/ en el directorio actual
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Windows (Cmd)
.venv\Scripts\activate.bat
```

#### Instalar dependencias del proyecto

```bash
uv sync                        # lee pyproject.toml y sincroniza el entorno
```

#### Añadir una dependencia nueva

```bash
uv add numpy
```

---

### 4) venv integrado (opción alternativa)

Si prefieres usar únicamente herramientas de la biblioteca estándar de Python:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Dentro del venv, usa pip
pip install -U pip
pip install -r requirements.txt  # si existe
```

---

### 5) Poetry (alternativa a uv)

Instalar Poetry:

- macOS/Linux:

```bash
# Opción 1: instalador oficial (recomendado)
curl -sSL https://install.python-poetry.org | python3 -

# Opción 2: pipx
pipx install poetry

# Opción 3: Homebrew
brew install poetry
```

- Windows (PowerShell):

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Crear/activar entorno e instalar:

```bash
poetry --version
poetry env use python
poetry install --no-root

# Ejecutar comandos dentro del entorno de Poetry
poetry run python -V
poetry add numpy
```

---

### 6) Guía rápida de activación

| Sistema | Comando |
|---|---|
| macOS/Linux (bash/zsh) | `source .venv/bin/activate` |
| Windows (PowerShell) | `.\.venv\Scripts\Activate.ps1` |
| Windows (Cmd) | `.venv\Scripts\activate.bat` |
| Poetry | `poetry run ...` o `poetry shell` |
| Desactivar (todos) | `deactivate` |
