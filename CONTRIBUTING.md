# Guia de Contribucion

Este repositorio es un fork de [CamilaCortex/MLOps_UdM](https://github.com/CamilaCortex/MLOps_UdM).
Las instrucciones a continuacion documentan el flujo de trabajo para desarrollar sobre **este fork**
sin afectar el repositorio original.

---

## Remotes

| Remote | Repositorio | Uso |
|--------|------------|-----|
| `origin` | `dpalacioj/MLOps-Course` | Tu fork — aqui haces push |
| `upstream` | `CamilaCortex/MLOps_UdM` | Repo original — para traer cambios de Camila |

Verificar configuracion:

```bash
git remote -v
```

## Sincronizar con el repo original

Cuando Camila publique cambios que quieras incorporar:

```bash
git fetch upstream
git merge upstream/main
```

O si prefieres traer solo commits especificos:

```bash
git fetch upstream
git cherry-pick <commit-hash>
```

## Crear ramas

Seguimos [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
Las ramas deben tener el formato `<tipo>/<descripcion-en-kebab-case>`:

```bash
# Ejemplos validos
git checkout -b feat/add-monitoring-module
git checkout -b fix/mlflow-tracking-bug
git checkout -b docs/update-readme

# Esto sera rechazado por el hook pre-push
git checkout -b mi-rama-nueva       # falta el tipo
git checkout -b feature/Add_Thing   # debe ser kebab-case en minusculas
```

Tipos permitidos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`, `hotfix`, `release`

## Hacer commits

Los mensajes de commit deben seguir el formato:

```
<tipo>[scope opcional]: <descripcion>
```

```bash
# Ejemplos validos
git commit -m "feat: add monitoring module with Evidently"
git commit -m "fix(tracking): correct MLflow metric logging"
git commit -m "docs: update course overview"
git commit -m "feat!: redesign experiment pipeline"   # breaking change

# Esto sera rechazado por el hook commit-msg
git commit -m "updated stuff"
git commit -m "fix bug"           # falta el ':'  y la descripcion
```

El hook `.githooks/commit-msg` valida automaticamente el formato.

## Crear Pull Requests

Por ser un fork, GitHub redirige los PRs hacia el repo de Camila por defecto.
Para crear PRs en **este fork**, siempre especificar `--repo`:

```bash
gh pr create \
  --repo dpalacioj/MLOps-Course \
  --base main \
  --head nombre-de-tu-rama \
  --title "tipo: descripcion del PR"
```

Si usas la interfaz web de GitHub, asegurate de cambiar el dropdown **"base repository"**
de `CamilaCortex/MLOps_UdM` a `dpalacioj/MLOps-Course` antes de crear el PR.

## Setup para nuevos clones

Si clonas este repo desde cero, configura los hooks y el upstream:

```bash
git clone git@github.com:dpalacioj/MLOps-Course.git
cd MLOps-Course
git remote add upstream https://github.com/CamilaCortex/MLOps_UdM.git
git config core.hooksPath .githooks
```
