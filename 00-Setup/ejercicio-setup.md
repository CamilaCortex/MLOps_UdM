# Ejercicio Practico: Configura tu Entorno MLOps

## Objetivo

Verificar que tienes un entorno de desarrollo funcional y listo para el curso.
Al finalizar, tendras un repositorio personal con todas las herramientas configuradas.

## Instrucciones

### Parte 1: Git y GitHub (15 min)

1. Crea un repositorio **privado** en GitHub llamado `mlops-setup-test`
2. Clonalo en tu maquina local
3. Crea una rama llamada `feat/initial-setup`

### Parte 2: Python y uv (15 min)

4. Dentro del repositorio clonado, inicializa un proyecto con `uv`:

```bash
uv init
```

5. Instala las siguientes dependencias:

```bash
uv add pandas scikit-learn matplotlib
```

6. Agrega `ruff` como dependencia de desarrollo:

```bash
uv add --dev ruff
```

7. Crea un archivo `main.py` con el siguiente contenido:

```python
import pandas as pd
from sklearn.datasets import load_iris

def load_and_describe():
    """Carga el dataset Iris y muestra un resumen."""
    iris = load_iris(as_frame=True)
    df = iris.frame
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nDescripcion estadistica:\n{df.describe()}")
    return df

if __name__ == "__main__":
    load_and_describe()
```

8. Ejecutalo para verificar que todo funciona:

```bash
uv run python main.py
```

### Parte 3: Calidad de codigo (10 min)

9. Ejecuta ruff sobre tu archivo:

```bash
uv run ruff check main.py
uv run ruff format main.py
```

10. Si ruff reporta algun issue, corrigelo.

### Parte 4: Commit y push (10 min)

11. Agrega todos los archivos relevantes y haz commit:

```bash
git add main.py pyproject.toml uv.lock .python-version
git commit -m "feat: initial project setup with uv and sklearn"
```

12. Haz push y crea un Pull Request hacia `main`:

```bash
git push -u origin feat/initial-setup
```

## Resultado esperado

Al finalizar deberias tener:

- Un repositorio en GitHub con una rama `feat/initial-setup`
- Un `pyproject.toml` con las dependencias del curso
- Un `uv.lock` generado automaticamente
- Un script `main.py` que carga un dataset y muestra un resumen
- Ruff ejecutandose sin errores
- Un PR abierto en tu repositorio

### Output esperado de `main.py`

```
Dataset shape: (150, 5)
Columns: ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)', 'target']

Descripcion estadistica:
       sepal length (cm)  sepal width (cm)  ...  petal width (cm)      target
count         150.000000        150.000000  ...        150.000000  150.000000
mean            5.843333          3.057333  ...          1.199333    1.000000
std             0.828066          0.435866  ...          0.762238    0.819232
...
```

## Criterios de evaluacion

| Criterio | Peso |
|----------|------|
| Repositorio creado y clonado correctamente | 20% |
| Proyecto inicializado con `uv` (pyproject.toml + uv.lock) | 20% |
| Dependencias instaladas correctamente | 20% |
| Script ejecuta sin errores | 20% |
| Ruff pasa sin errores y PR creado | 20% |
