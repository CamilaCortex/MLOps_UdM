---
description: Revisa y deja lista una sesión del curso (orden, claridad, docs vigentes, verificación real)
---

Trabaja sobre la sesión: **$ARGUMENTS**

Tu tarea es dejar esa sesión lista para dictarse: navegable en orden, entendible por alguien que no sabe del tema, alineada con la documentación vigente de cada herramienta, y **verificada ejecutándola**. Antes de tocar nada, lee el README de la sesión y lista los archivos para entender qué hay.

## 1. El orden tiene que verse sin leer nada

- Todo archivo que forme parte de una secuencia lleva **prefijo numérico** (`01-`, `02-`… con cero a la izquierda si hay diez o más) y un nombre que diga **qué agrega**, no de qué trata.
- La secuencia vive en **una sola carpeta**. Si está repartida entre dos, `ls` no muestra el orden y el estudiante no puede saber por dónde empezar: unifícala.
- El material que **no** tiene orden entre sí (complementos, referencias) va en carpeta aparte y **sin numerar**. Numerar algo que no es secuencial es mentir.
- Una sola convención de nombres en la carpeta: o todo kebab-case o todo snake_case, no mezclado.
- El README abre con una tabla **"El recorrido"**: paso, qué archivo se abre, para qué, y si **bloquea la terminal**. Es lo primero que se consulta en vivo.
- Si renombras o mueves algo, usa `git mv` y **actualiza todas las referencias del repositorio** (`grep -rIn` del nombre viejo antes y después). Incluye READMEs, docstrings, notebooks, YAML de configuración, guiones de `instructor/` y `src/`. No debe quedar ni una mención al nombre anterior.
- Los números escritos en la prosa y en los docstrings (`"Paso 4 de la progresión"`) tienen que coincidir con el nombre del archivo. Es lo primero que se desincroniza al renombrar.

## 2. Escrito para quien no sabe

El lector no conoce la herramienta ni el vocabulario. Leyendo el archivo, solo, tiene que entender.

- Explica **el mecanismo, no el nombre**. "Un decorador es una función que recibe una función y devuelve otra" enseña; "usamos el decorador `@task`" no.
- Cuando algo tiene un nombre técnico opaco, di primero **qué hace** y después cómo se llama.
- Una analogía por concepto difícil, concreta y del mundo real. No más de una: dos analogías para lo mismo confunden.
- Di **qué se gana y qué cuesta**. Cada herramienta que se agrega tiene un precio (un servidor que levantar, un proceso que mantener); nombrarlo evita que el curso parezca publicidad.
- Nombra explícitamente **cuándo la herramienta NO hace falta**. Un curso que solo dice "usa esto" no enseña a decidir.
- Los comentarios de código explican **por qué**, no qué. `# suma 1` sobra; `# +1 porque el rango es inclusivo` sirve.

## 3. Alineado con la documentación vigente

- **Verifica contra la documentación oficial actual**, no contra tu memoria ni contra lo que dice el archivo. Si hay un MCP de documentación disponible (por ejemplo context7), úsalo; si no, busca la referencia oficial.
- Toda API deprecada fuera. Si aparece una, di cuál es la vigente y por qué cambió.
- Las versiones y las tablas comparativas llevan **fecha de evaluación** visible, porque envejecen.
- Nada de datos que envejecen mal como argumento (estrellas de GitHub, "la más popular").
- Si el repositorio ya tiene una tabla o un ADR que es la **única fuente** de algo, no la contradigas: cualquier diagrama o README que la refleje se regenera desde ella.

## 4. Nada de arqueología

**Prohibido comparar con versiones anteriores del curso o del repositorio.** Nada de "el repo anterior hacía X", "antes estaba mal", "bug corregido respecto a…". El estudiante no puede ver ese código y no le dice nada.

Cuando la enseñanza está en el error, escríbela **en presente y en prospectiva**: cuál es el atajo tentador, cómo se ve, y por qué falla. Así lo reconoce en su propio código, que es lo único que le sirve.

Excepción: los ADR, `docs/MIGRACION.md` y las auditorías. Ahí la comparación **es** el contenido del documento.

## 5. Verificar ejecutando, nunca afirmar

Esto es lo más importante y lo que más se salta.

- **Corre todos los archivos ejecutables de la sesión.** Un archivo que nadie ejecutó puede llevar meses roto en el repositorio y nadie lo sabe.
- Levanta lo que haga falta (servidor, worker, base de datos), ejecuta, y **pega la salida real** como evidencia de que funciona.
- Los que bloquean la terminal por diseño se prueban igual: lánzalos, dispáralos desde otra terminal, y comprueba el efecto.
- Si algo no se puede verificar, **dilo explícitamente** en el informe. No lo declares funcionando.
- Comprueba diferencias de plataforma: macOS no tiene `timeout`, `date` no es igual en BSD y GNU, hay carpetas protegidas por TCC (`~/Documents`, `~/Desktop`, `~/Downloads`), y en Windows no existe `cron`.
- **Limpia el estado que crees al verificar** (deployments, work pools, entradas de crontab, corridas de prueba) y dilo. No dejes la máquina con residuos de tus pruebas.
- Corre `pre-commit run` y la suite de tests antes de dar nada por terminado. Los hooks propios del curso son parte de la revisión, no un trámite.

## 6. Di qué debe ver el estudiante en pantalla

La mitad de las dudas en clase son "lo ejecuté y no pasó nada".

- Cada paso ejecutable dice **qué salida esperar**, con el texto real.
- Si lo correcto es que **no pase nada** (un módulo que solo define funciones, un proceso que se queda esperando), dilo con esas palabras y explica por qué.
- Si el argumento del paso es "mira el dashboard", **comprueba que el dashboard efectivamente lo muestre**. Una demo que no puede demostrar su propia afirmación es peor que no tenerla.
- Di **dónde** aparece la salida: en esta terminal, en la del worker, en la UI. Y si aparece fuera de orden, avísalo.
- Documenta los **errores esperables** con su mensaje literal, su causa y el arreglo. Y enseña a leer un traceback: la última línea es la útil, las cuarenta anteriores son ruido.
- Declara los **prerrequisitos**: qué terminal, qué tiene que estar corriendo, qué configuración hay que fijar — y si esa configuración es **permanente**, dilo y da el comando para revertirla.
- Todo lo que quede **persistente** (una línea de crontab, un deployment con schedule) lleva su instrucción de retirada. Enseñar a montar sin enseñar a desmontar deja máquinas trabajando de gratis durante meses.

## 7. Higiene del código

- **Cero `TODO`, `FIXME` o `XXX`** en código que no sea un ejercicio. Si ya está resuelto, bórralo; si describe una rama de *fallback*, di que es un fallback y qué pierde frente al camino normal.
  Se conserva intacto el andamiaje deliberado de ejercicios (`TODO(estudiante) NN`, `TODO 1..9`): está numerado y documentado a propósito.
- **Ninguna ruta absoluta.** Se resuelven en tiempo de ejecución desde `__file__`. Una ruta que arranque en el home de alguien funciona en un solo disco del mundo.
- **Ningún secreto**, ni de ejemplo. Los secretos se leen del entorno; lo que se versiona es el nombre, nunca el valor.
- **Ninguna métrica inventada.** Si el ejemplo no entrena nada, no finjas métricas: usa datos verificables a mano o muestra solo la mecánica.
- **Nada de terceros frágiles** en las demos. Una demo de resiliencia que depende de un endpoint público falla en clase por el motivo equivocado. Los fallos se simulan en local y de forma determinista.
- **No dupliques el pipeline.** La fuente de verdad vive en `src/taxi/`; el material de la sesión **importa** de ahí. Una copia por sesión son features distintas entrenando modelos distintos y ninguna fuente de verdad.

## 8. Entregable

Cuando todo esté verificado:

- Commits en **conventional commits**, mensaje en español, minúscula tras los dos puntos, cuerpo que explique **por qué** y no solo qué.
- **El autor es siempre el usuario.** Nunca te atribuyas autoría: sin `Co-Authored-By`, sin "generated with", sin mención a Claude.
- **Separa tus cambios de los que el usuario ya tenía en curso.** Revisa `git status` antes de empezar. Si un archivo mezcla ambos, extrae solo tus hunks (`git diff` → filtra → `git apply --cached`) y deja los suyos sin comitear.
- Agrupa por tema, con granularidad moderada: ni un commit gigante ni uno por archivo.
- Las soluciones de talleres y ejercicios (`sesiones/*/_soluciones/`) **nunca se versionan**: están en `.gitignore` y se quedan en local.

## 9. Informe final

Reporta con honestidad, sin adornos:

- qué cambiaste y por qué;
- **qué ejecutaste y qué salida dio**;
- **qué no pudiste verificar**, y por qué;
- qué encontraste roto que no estaba en el encargo;
- qué dejaste sin tocar deliberadamente.

Si te equivocas en el camino, corrígelo y sigue. Si una afirmación tuya depende de mirar una interfaz o correr un comando, **míralo o córrelo** antes de afirmarla.
