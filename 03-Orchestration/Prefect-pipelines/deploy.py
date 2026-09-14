#!/usr/bin/env python
"""
Deployment configuration for NYC Taxi Duration Prediction Pipeline.

Reentrena el modelo una vez al mes, usando siempre el periodo de datos más
reciente que la TLC ya tenga publicado (ver find_latest_available_period en
src/data/utils.py) en vez de un year/month fijo. Así este mismo deployment
sigue siendo correcto mes tras mes, sin necesidad de volver a desplegarlo
cada vez que sale un mes nuevo de datos.
"""

import logging

from prefect.client.schemas.schedules import CronSchedule

from pipeline import duration_prediction_flow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting monthly retraining deployment...")
    logger.info("Name: monthly-retraining")
    logger.info("Schedule: 0 6 5 * * (día 5 de cada mes, 6:00am America/Bogota)")
    logger.info("Periodo de entrenamiento: se detecta automáticamente en cada corrida")
    logger.info("  (ver find_latest_available_period en src/data/utils.py)")

    # A propósito NO se pasan 'parameters' con year/month fijos: al dejarlos
    # en None, duration_prediction_flow calcula en cada ejecución cuál es el
    # periodo más reciente realmente disponible en la TLC. El día 5 del mes
    # es solo un margen de seguridad razonable, no una garantía -si ese día
    # la TLC todavía no publicó el mes esperado, el pipeline retrocede
    # automáticamente al último mes disponible en vez de fallar con un 403.
    duration_prediction_flow.serve(
        name="monthly-retraining",
        schedule=CronSchedule(cron="0 6 5 * *", timezone="America/Bogota"),
        tags=["production", "monthly", "ml", "auto-period"],
        description=(
            "Reentrena el modelo una vez al mes con el periodo de datos más "
            "reciente disponible en la TLC, detectado automáticamente en "
            "cada corrida (no un year/month fijo)."
        ),
    )

    logger.info("Deployment is now running.")
    logger.info("The server is running and will execute the flow:")
    logger.info("  - El día 5 de cada mes a las 6:00am (America/Bogota)")
    logger.info("  - Press Ctrl+C to stop")
    logger.info("View executions at:")
    logger.info("  - Prefect Cloud: https://app.prefect.cloud")
    logger.info("  - Or local UI: http://localhost:4200")
    logger.info("Nota: el día 5 es un margen de seguridad, no una garantía -")
    logger.info("si ese día la TLC aún no publicó el mes esperado, el")
    logger.info("pipeline retrocede automáticamente al último mes disponible.")
