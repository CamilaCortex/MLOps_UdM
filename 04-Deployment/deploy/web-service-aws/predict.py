"""
API REST con Flask para predicción de duración de viajes de taxi en NYC.

Pensada para correr detrás de gunicorn dentro de un contenedor Docker
desplegado en una instancia EC2 de AWS (ver GUIA_AWS_EC2.md) y probarse
desde Postman.
"""

import logging

from flask import Flask, jsonify, request

from src.model_loader import model_loader

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

REQUIRED_FIELDS = ('PULocationID', 'DOLocationID', 'trip_distance')

# El modelo se carga una sola vez, al importar este módulo (tanto gunicorn
# como "python predict.py" importan el módulo antes de servir requests).
logging.info("Cargando modelo...")
model_loader.load()
logging.info("API lista para recibir requests")

app = Flask('duration-prediction')


def _trip_to_feature(ride: dict) -> dict:
    """
    Convierte el JSON recibido en el dict de features que espera el
    preprocessor (mismo formato usado en entrenamiento: PU_DO combinado
    + trip_distance).
    """
    return {
        'PU_DO': f"{ride['PULocationID']}_{ride['DOLocationID']}",
        'trip_distance': ride['trip_distance'],
    }


@app.route('/health', methods=['GET'])
def health():
    """Health check: confirma que el modelo está cargado y funcionando."""
    is_loaded = model_loader.is_loaded()

    body = {
        'status': 'healthy' if is_loaded else 'unhealthy',
        'model_loaded': is_loaded,
    }
    if is_loaded:
        body.update({
            'model_name': model_loader.metadata['model_name'],
            'model_version': str(model_loader.metadata['version']),
            'model_rmse': model_loader.metadata['rmse'],
        })

    return jsonify(body), (200 if is_loaded else 503)


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    """Predice la duración de un viaje de taxi a partir del JSON recibido."""
    ride = request.get_json(silent=True)

    if ride is None:
        return jsonify({
            'error': "El body debe ser JSON valido (header Content-Type: application/json)"
        }), 400

    missing = [field for field in REQUIRED_FIELDS if field not in ride]
    if missing:
        return jsonify({
            'error': f"Faltan campos requeridos: {', '.join(missing)}"
        }), 400

    try:
        features = _trip_to_feature(ride)
        prediction = model_loader.predict([features])[0]
    except Exception as e:
        logging.error("Error al hacer la predicción: %s", e)
        return jsonify({'error': f"Error al hacer la predicción: {e}"}), 500

    result = {
        'duration': round(prediction, 2),
        'pickup_location': ride['PULocationID'],
        'dropoff_location': ride['DOLocationID'],
        'trip_distance': ride['trip_distance'],
        'model_name': model_loader.metadata['model_name'],
        'model_version': str(model_loader.metadata['version']),
    }

    return jsonify(result)


if __name__ == "__main__":
    # Solo para pruebas locales rápidas sin gunicorn; en Docker/EC2 se usa
    # el ENTRYPOINT del Dockerfile (gunicorn --bind=0.0.0.0:9696 predict:app).
    app.run(debug=False, host='0.0.0.0', port=9696)
