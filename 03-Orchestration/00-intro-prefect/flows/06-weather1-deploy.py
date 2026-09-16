import httpx
from prefect import flow


@flow(log_prints=True)
def fetch_weather(lat: float = 38.9, lon: float = -77.0):
    base_url = "https://api.open-meteo.com/v1/forecast/"
    temps = httpx.get(
        base_url,
        params=dict(latitude=lat, longitude=lon, hourly="temperature_2m"),
    )
    forecasted_temp = float(temps.json()["hourly"]["temperature_2m"][0])
    print(f"Forecasted temp C: {forecasted_temp} degrees")
    return forecasted_temp


if __name__ == "__main__":
    fetch_weather.from_source(
        source="https://github.com/CamilaCortex/MLOps_UdM",
        entrypoint="03-Orchestration/00-intro-prefect/flows/06-weather1-deploy.py:fetch_weather",
    ).deploy(
        name="weather-deployment",
        cron="*/10 * * * *",
        parameters={"lat": 6.2476, "lon": -75.5658},
        work_pool_name="default-worker-pool",  # sin espacio al final
    )