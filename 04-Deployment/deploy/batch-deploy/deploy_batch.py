"""
Script para crear y servir deployment automático de batch predictions.
Se ejecuta cada hora con 1000 viajes.
"""

import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.prefect_flows import scheduled_batch_flow

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

if __name__ == "__main__":
    logging.info("="*60)
    logging.info("DEPLOYMENT AUTOMÁTICO - BATCH PREDICTIONS")
    logging.info("="*60)
    logging.info("Configuración:")
    logging.info("  Nombre: batch-prediction-hourly")
    logging.info("  Frecuencia: Cada hora (0 * * * *)")
    logging.info("  Viajes por batch: 1000")
    logging.info("="*60)
    logging.info("Iniciando deployment...")
    logging.info("Presiona Ctrl+C para detener")
    logging.info("="*60)
    
    # Servir el flow con schedule
    scheduled_batch_flow.serve(
        name="batch-prediction-hourly",
        cron="0 * * * *",  # Cada hora
        description="Predicciones batch automáticas cada hora con 1000 viajes"
    )
