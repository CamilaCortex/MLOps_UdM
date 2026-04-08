import pickle

from flask import Flask, request, jsonify

with open('lin_reg.bin', 'rb') as f_in:
    """Carga el modelo"""
    (dv, model) = pickle.load(f_in)


def prepare_features(ride):
    """Prepara las características para la predicción.

    Args:
        ride (dict): Un diccionario con las características de la predicción.

    Returns:
        dict: Un diccionario con las características preparadas.
    """
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    """Realiza la predicción de la duración de la carrera.

    Args:
        features (dict): Un diccionario con las características de la predicción.

    Returns:
        float: La predicción de la duración de la carrera.
    """
    X = dv.transform(features)
    preds = model.predict(X)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    """Endpoint para la predicción de la duración de la carrera."""
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred
    }

    return jsonify(result)


if __name__ == "__main__":
    """Función principal que ejecuta la aplicación."""
    app.run(debug=True, host='0.0.0.0', port=9696)