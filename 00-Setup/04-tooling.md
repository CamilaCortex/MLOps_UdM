## Herramientas: Editor, Linters, Formateadores, Pre-commit

### Editor (VS Code recomendado -- Free!)

- Instala VS Code: `https://code.visualstudio.com/`

#### Extensiones recomendadas

| Extensión | ID | ¿Qué hace? |
|---|---|---|
| **Python** | `ms-python.python` | Soporte base de Python en VS Code: ejecutar scripts, depurar, seleccionar intérpretes, notebooks |
| **Pylance** | `ms-python.vscode-pylance` | Autocompletado inteligente, detección de errores de tipo y navegación de código (va a definiciones, encuentra referencias) |
| **Ruff** | `charliermarsh.ruff` | Linter + formateador ultrarrápido. Detecta errores, imports sin usar y formatea tu código automáticamente al guardar |
| **Black Formatter** | `ms-python.black-formatter` | Formateador de código opinionado (un solo estilo, sin configurar nada). Alternativa a Ruff para formateo |

#### Extensiones opcionales (útiles en el día a día)

| Extensión | ID | ¿Qué hace? |
|---|---|---|
| **autoDocstring** | `njpwerner.autodocstring` | Genera automáticamente la estructura del docstring de una función. Escribes `"""` y te llena los parámetros y el return |
| **Flake8** | `ms-python.flake8` | Linter clásico de Python. Ruff lo reemplaza (y es más rápido), pero muchos proyectos aún lo usan |
| **GitGraph** | `mhutchie.git-graph` | Muestra el historial de Git como un gráfico visual con ramas, merges y commits. Útil para entender qué pasó en el repo |
| **GitLens** | `eamodio.gitlens` | Muestra quién modificó cada línea y cuándo (blame), compara versiones y navega el historial de cualquier archivo |

> **Nota:** Ruff y Black hacen cosas similares (formatear código). No necesitas
> ambos — elige uno. En este curso usamos **Ruff** porque además de formatear,
> también hace lint (detecta errores).

### Ruff y Black

Con uv:

```bash
uv add --dev ruff black
uv run ruff --version
uv run black --version

# Comprobar formato y lint
uv run ruff check .
uv run black --check .
```

Con Poetry:

```bash
poetry add -G dev ruff black
poetry run ruff check .
poetry run black --check .
```

### Hooks de pre-commit

#### ¿Qué es un hook?

Un **hook** (gancho) es un script que Git ejecuta **automáticamente** en un
momento específico. En este caso, usamos hooks de **pre-commit**: se ejecutan
justo _antes_ de que se complete un `git commit`. Si algún hook falla, el
commit se cancela y te muestra qué hay que corregir.

Piensa en esto como un **control de calidad automático** que revisa tu código
cada vez que intentas guardar un cambio en Git. Por ejemplo:

- ¿Dejaste un `import numpy` sin usar? El hook lo detecta.
- ¿Tu código tiene formato inconsistente? El hook lo corrige.
- ¿Estás subiendo un archivo de 50 MB por accidente? El hook lo bloquea.

#### Configuración paso a paso

1) Copia la plantilla a la raíz del proyecto:

```bash
cp 00-Setup/templates/pre-commit-config.yaml .pre-commit-config.yaml
```

> Abre ese archivo y lee los comentarios — explica qué hace cada hook.

2) Instala pre-commit en tu entorno y activa los hooks:

- uv:

```bash
uv add --dev pre-commit
uv run pre-commit install
```

- pip (venv):

```bash
pip install pre-commit
pre-commit install
```

- Poetry:

```bash
poetry add -G dev pre-commit
poetry run pre-commit install
```

3) A partir de ahora, cada `git commit` ejecutará los checks. Si quieres
   ejecutarlos manualmente sin hacer commit:

```bash
pre-commit run --all-files
```

#### ¿Qué pasa cuando un hook falla?

```
$ git commit -m "feat: add model"
ruff.....................................................Failed
- hook id: ruff
- files were modified by this hook

Fixed 1 error:
  src/model.py: removed unused import `os`
```

El commit **no se realizó**. Ruff corrigió el archivo automáticamente. Solo
necesitas volver a agregar los cambios y commitear de nuevo:

```bash
git add .
git commit -m "feat: add model"   # ahora sí pasa
```
