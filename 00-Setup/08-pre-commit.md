# Pre-commit: Automatizando la Calidad del Codigo

## Que es pre-commit?

`pre-commit` es un framework que ejecuta **verificaciones automaticas** cada vez que haces
`git commit`. Si alguna verificacion falla, el commit se bloquea hasta que corrijas el problema.

Piensa en pre-commit como un **guardian** que revisa tu codigo antes de que entre al
repositorio. Es como tener un revisor automatico que nunca se cansa.

## Para que sirve?

| Sin pre-commit | Con pre-commit |
|----------------|----------------|
| "Se me olvido formatear" | El formateador corre automaticamente |
| "Subi un archivo de 200MB" | Se bloquea y te avisa |
| "Commiteé mi API key" | Gitleaks lo detecta y bloquea |
| "Hay conflictos de merge" | Detecta marcadores `<<<<<<<` |
| "El linter fallo en CI" | Ya fallo local, antes de subir |

En resumen: **atrapa errores antes de que se vuelvan problemas**.

## Como funciona internamente?

Cuando ejecutas `git commit`, Git tiene "hooks" — puntos donde puede ejecutar
scripts automaticamente. Pre-commit se instala en el hook `pre-commit` (de ahi su nombre).

El flujo es:

```
git commit -m "mi cambio"
      |
      v
[Hook pre-commit se activa]
      |
      v
[Ejecuta cada verificacion configurada]
      |
      +---> trailing-whitespace: elimina espacios al final
      +---> check-yaml: valida archivos YAML
      +---> ruff: lint + auto-fix de Python
      +---> ruff-format: formateo consistente
      +---> gitleaks: busca secretos (API keys, tokens)
      |
      v
[Todas pasaron?]
      |
  SI -+-> Commit se ejecuta normalmente
      |
  NO -+-> Commit se bloquea, muestra que fallo
           (algunos hooks auto-corrigen y solo necesitas re-commitear)
```

**Dato importante**: pre-commit solo revisa los archivos que estan en staging (`git add`).
No revisa todo el repositorio cada vez — solo lo que vas a commitear.

## Instalacion y uso

### Paso 1: Instalar pre-commit

```bash
# Con uv (recomendado)
uv add --dev pre-commit

# Con pip
pip install pre-commit
```

### Paso 2: Activar los hooks en tu repositorio

```bash
# Esto instala los hooks en .git/hooks/
uv run pre-commit install
```

A partir de ahora, cada `git commit` ejecutara las verificaciones automaticamente.

### Paso 3: Ejecutar manualmente (opcional)

```bash
# Correr sobre todos los archivos (util la primera vez)
uv run pre-commit run --all-files

# Correr un hook especifico
uv run pre-commit run ruff --all-files
```

### Paso 4: Actualizar versiones de los hooks

```bash
uv run pre-commit autoupdate
```

## Que verificaciones usamos en este proyecto?

El archivo `.pre-commit-config.yaml` en la raiz del repositorio define las verificaciones:

### Hooks de higiene general

| Hook | Que hace |
|------|----------|
| `trailing-whitespace` | Elimina espacios invisibles al final de las lineas |
| `end-of-file-fixer` | Asegura que cada archivo termine con una linea en blanco |
| `check-yaml` | Valida que los archivos `.yml`/`.yaml` tengan sintaxis correcta |
| `check-added-large-files` | Bloquea archivos mayores a 500KB (usa Git LFS para esos) |
| `check-merge-conflict` | Detecta marcadores de conflicto (`<<<<<<<`) que olvidaste resolver |

### Linting y formateo con Ruff

| Hook | Que hace |
|------|----------|
| `ruff` | Analiza el codigo Python buscando errores, imports sin usar, estilo inconsistente. Aplica auto-fix cuando puede. |
| `ruff-format` | Formatea el codigo Python de manera consistente (similar a Black pero mas rapido). |

**Por que Ruff?** Es un linter escrito en Rust que reemplaza flake8, isort, pyflakes y black.
Es 10-100x mas rapido y combina multiples herramientas en una sola.

### Seguridad

| Hook | Que hace |
|------|----------|
| `gitleaks` | Escanea el codigo buscando secretos: API keys, tokens, passwords. Si detecta uno, bloquea el commit. |

## Cuando algo falla

```bash
$ git commit -m "feat: add new feature"
trailing-whitespace.................................................Passed
end-of-file-fixer...................................................Passed
check-yaml..........................................................Passed
ruff................................................................Failed
- hook id: ruff
- files were modified by this hook    # <-- Ruff auto-corrigio algo
```

En este caso, Ruff detecto un problema y lo corrigio automaticamente.
Solo necesitas:

```bash
git add .           # Re-agregar los archivos corregidos
git commit -m "feat: add new feature"   # Intentar de nuevo
```

## Preguntas frecuentes

**Puedo saltarme pre-commit?**
Si, con `git commit --no-verify`. Pero no es recomendable — los hooks estan ahi para protegerte.

**Afecta la velocidad de los commits?**
La primera vez descarga las herramientas (unos segundos). Despues, cada commit tarda 1-3 segundos adicionales.

**Funciona en CI/CD tambien?**
Si. GitHub Actions puede ejecutar `pre-commit run --all-files` como parte del pipeline.
Pero la idea es que los errores se atrapen **antes** de hacer push.
