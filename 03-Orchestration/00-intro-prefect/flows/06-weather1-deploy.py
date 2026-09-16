import httpx
from pathlib import Path
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
    # .serve() no necesita work pool, imagen ni repo remoto: el propio
    # script queda corriendo como el "worker" y reporta a Prefect Cloud.
    fetch_weather.serve(
        name="weather-deployment",
        cron="*/10 * * * *",
        parameters={"lat": 6.2476, "lon": -75.5658},
    )
