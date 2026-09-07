"""
Ejemplo de reintentos automaticos con Prefect.

Simula una operacion que falla de forma aleatoria, sin depender de ningun
servicio externo, para demostrar el mecanismo de retries de forma
reproducible y sin conexion a internet.
"""

import random

from prefect import flow, task


@task(retries=4, retry_delay_seconds=2, log_prints=True)  # tambien puede ser una lista, p. ej. [1, 2, 5]
def fetch_random_code():
    """Simula una respuesta que falla (500) o tiene exito (200) al azar."""
    status = random.choice([200, 500])

    if status >= 400:
        raise Exception(f"Simulated failure with status code: {status}")

    print(f"Success! Status: {status}")


@flow(log_prints=True)
def fetch():
    fetch_random_code()


if __name__ == "__main__":
    fetch()
