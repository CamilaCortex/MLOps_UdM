import httpx
from prefect import flow, task
from prefect.artifacts import create_table_artifact
import pandas as pd


@task
def fetch_weather(lat: float, lon: float):
    base_url = "https://api.open-meteo.com/v1/forecast/"
    temps = httpx.get(
        base_url,
        params=dict(latitude=lat, longitude=lon, hourly="temperature_2m"),
    )
    forecasted_temp = float(temps.json()["hourly"]["temperature_2m"][0])
    print(f"Forecasted temp C: {forecasted_temp} degrees")
    return forecasted_temp


@task
def save_weather(temp: float):
    with open("weather.csv", "w+") as w:
        w.write(str(temp))
    
    # Crear artifact en Prefect Cloud
    df = pd.DataFrame({"temperature_celsius": [temp]})
    create_table_artifact(
        key="weather-data",
        table=df.to_dict('records'),
        description="Weather temperature data"
    )
    
    return "Successfully wrote temp"


@flow(retries=3, log_prints=True)
def pipeline(lat: float = 38.9, lon: float = -77.0):
    temp = fetch_weather(lat, lon)
    result = save_weather(temp)
    print(result)
    return result


if __name__ == "__main__":
    pipeline()


# export PREFECT_LOGGING_LOG_PRINTS=True
  