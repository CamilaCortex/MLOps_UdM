"""
Script simple para probar la API sin necesidad de Postman.

Uso:
    python test.py                          # prueba contra localhost:9696
    python test.py http://<dns-público-ec2>:9696   # prueba contra EC2
"""

import sys

import requests

base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:9696'

ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 4.0
}

print(f"Probando API en: {base_url}\n")

print("1. Health check")
health_response = requests.get(f"{base_url}/health")
print(f"   Status: {health_response.status_code}")
print(f"   Body:   {health_response.json()}\n")

print("2. Predicción")
predict_response = requests.post(f"{base_url}/predict", json=ride)
print(f"   Status: {predict_response.status_code}")
print(f"   Body:   {predict_response.json()}")
