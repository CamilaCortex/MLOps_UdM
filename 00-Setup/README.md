## 00-Setup: Puesta a punto de entorno y flujo de trabajo

Esta carpeta es tu punto de partida para el curso. Te ayuda a preparar un entorno de desarrollo fiable y reproducible con Git/GitHub y Python utilizando herramientas modernas de dependencias.

Puedes usar uv (rápido y sencillo) o Poetry (más completo). En este curso recomendamos uv por su rapidez y excelentes instalaciones reproducibles, pero también incluimos instrucciones para Poetry.

### Inicio rápido (recomendado: uv)

- macOS (zsh/bash):

```bash
# 1) Instalar Git
brew install git

# 2) Instalar Python 3.11 con pyenv
brew install pyenv
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
exec "$SHELL"
pyenv install 3.11.9
pyenv global 3.11.9

# 3) Instalar uv
brew install uv

# 4) Clonar el repo del curso (reemplaza con tu fork)
git clone <your-repo-url>
cd <repo-name>

# 5) Crear y activar entorno virtual
uv venv
source .venv/bin/activate

# 6) (Si existe pyproject.toml) instalar dependencias
uv sync

# 7) Verificar
python -V
uv --version
```

- Windows (PowerShell como Administrador):

```powershell
# 1) Instalar Git
winget install --id Git.Git -e --source winget

# 2) Instalar Python 3.11 con pyenv-win
Invoke-WebRequest -UseBasicParsing `
  -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" `
  -OutFile "./install-pyenv-win.ps1"; & "./install-pyenv-win.ps1"
# Cierra y abre la terminal, luego:
pyenv install 3.11.9
pyenv global 3.11.9

# 3) Instalar uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 4) Clonar el repo del curso (reemplaza con tu fork)
git clone <your-repo-url>
cd <repo-name>

# 5) Crear y activar entorno virtual
uv venv
.\.venv\Scripts\Activate.ps1

# 6) (Si existe pyproject.toml) instalar dependencias
uv sync

# 7) Verificar
python -V
uv --version
```

Si prefieres Poetry o venv, consulta `02-python-envs.md` y `03-dependency-management.md`.

### Qué aprenderás aquí

- Fundamentos de Git y GitHub: instalación, autenticación SSH, ramas y PRs
- Entornos de Python: venv básico, uv y Poetry
- Gestión de dependencias: instalación, bloqueo y reproducción de entornos
- Herramientas: configuración del editor, calidad de código (ruff/black), hooks de pre-commit
- Reproducibilidad e integración continua con GitHub Actions

### Contenidos

- `01-git-github.md`: Instalación de Git/GitHub, SSH, flujos de trabajo y PRs
- `01.1-conventional-commits.md`: Guía de Conventional Commits y nomenclatura de ramas
- `02-python-envs.md`: Instalación de Python, entornos virtuales (uv, venv, Poetry)
- `02.1-uv-conda-venv.md`: Comparación práctica entre uv, venv y Miniconda
- `03-dependency-management.md`: Gestión y bloqueo de dependencias con uv y Poetry
- `04-tooling.md`: VS Code, extensiones, ruff, pre-commit hooks
- `05-data-and-secrets.md`: Archivos .env y protección de secretos (local y CI)
- `06-github-actions.md`: CI de ejemplo para uv y Poetry
- `07-os-notes.md`: Consejos para macOS y Windows (shells, rutas, permisos)
- `08-pre-commit.md`: Configuración de hooks de pre-commit
- `09-cicd-guide.md`: Guía de CI/CD
- `10-git-lfs.md`: Git LFS para archivos grandes (modelos, imágenes, datasets)
- `ejercicio-setup.md`: Ejercicio práctico para verificar tu entorno
- `templates/`: ejemplos listos para copiar (pyproject, pre-commit, .gitignore)
- `scripts/`: scripts de configuración multiplataforma para uv y Poetry

### Cómo usar esta carpeta

- Sigue `01-03` en orden para una configuración fluida.
- Copia los archivos que necesites desde `templates/` a la raíz del proyecto (por ejemplo, `.pre-commit-config.yaml`, `.env.example`, workflows de CI).
- Ejecuta los scripts en `scripts/` si quieres una configuración guiada.

### Si necesitas ayuda

- Revisa de nuevo las notas específicas por sistema en `07-os-notes.md`.
- Confirma el comando correcto de activación del entorno para tu sistema operativo.
- Asegúrate de estar dentro del entorno virtual antes de instalar o ejecutar nada.
