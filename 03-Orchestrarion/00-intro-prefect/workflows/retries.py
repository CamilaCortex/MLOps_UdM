import httpx
from prefect import flow, task
import random


@task(retries=4, retry_delay_seconds=2)  # or [1, 2, 5])
def fetch_random_code():
    # Simular respuestas aleatorias 200 o 500
    status = random.choice([200, 500])
    random_code = httpx.get(f"https://tools-httpstatus.pickup-services.com/{status}")
    
    if random_code.status_code >= 400:
        raise Exception(f"Got status code: {random_code.status_code}")
    
    print(f"Success! Status: {random_code.status_code}")


@flow
def fetch():
    fetch_random_code()


if __name__ == "__main__":
    fetch()
