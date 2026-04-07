"""
Prefect flows para batch prediction usando modelo local.
Versión simplificada que usa modelo copiado del pipeline.
"""

from datetime import datetime
from prefect import flow, task, get_run_logger
from prefect.artifacts import create_markdown_artifact, create_table_artifact
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_generator import generate_taxi_data, save_batch_data
from src.batch_predictor import process_batch_file
from src.database import get_database


@task(name="generate-taxi-data", description="Generar datos de viajes de taxi")
def generate_data_task(num_trips: int = None):
    """
    Genera datos de viajes de taxi.

    Args:
        num_trips: Número de viajes a generar

    Returns:
        Path al archivo guardado
    """
    logger = get_run_logger()
    logger.info("Generando datos de viajes de taxi...")

    df = generate_taxi_data(num_trips=num_trips)
    filepath = save_batch_data(df)

    logger.info(f"Generados {len(df)} viajes")
    logger.info(f"Datos guardados en: {filepath}")

    return filepath


@task(name="process-batch-predictions", description="Procesar predicciones batch")
def process_predictions_task(input_file):
    """
    Procesa predicciones batch usando modelo local.

    Args:
        input_file: Path al archivo de datos

    Returns:
        Dictionary con resultados del procesamiento
    """
    logger = get_run_logger()
    logger.info(f"Procesando predicciones para: {input_file}")
    logger.info("Usando modelo local copiado del pipeline")
    logger.info("Guardando en base de datos SQL")

    result = process_batch_file(input_file)

    logger.info("Procesamiento batch completado")
    logger.info(f"   Viajes Procesados: {result['trips_processed']}")
    logger.info(f"   Registros Guardados: {result['records_saved']}")
    logger.info(f"   Batch ID: {result['batch_id']}")
    logger.info(f"   Modelo: {result['model_name']} v{result['model_version']}")

    return result


@task(name="create-prediction-summary", description="Crear resumen de predicciones")
def create_summary_artifact(result: dict):
    """
    Crea artifacts de Prefect con resumen de predicciones.

    Args:
        result: Dictionary con resultados del procesamiento
    """
    logger = get_run_logger()
    logger.info("Creando artifacts de resumen...")

    # Tabla con métricas clave
    metrics_data = [
        ["Métrica", "Valor"],
        ["Viajes Procesados", result["trips_processed"]],
        ["Registros Guardados", result["records_saved"]],
        ["Batch ID", result["batch_id"]],
        ["Modelo", result["model_name"]],
        ["Versión", result["model_version"]],
        ["RMSE del Modelo", f"{result['model_rmse']:.4f}"],
        ["Duración Promedio (min)", f"{result['avg_duration']:.2f}"],
        ["Duración Mínima (min)", f"{result['min_duration']:.2f}"],
        ["Duración Máxima (min)", f"{result['max_duration']:.2f}"],
    ]

    create_table_artifact(
        key="batch-prediction-metrics",
        table=metrics_data,
        description=f"Métricas de predicción batch para {result['batch_id']}",
    )

    # Markdown con resumen detallado
    markdown_content = f"""
    # Resumen de Predicciones Batch
    
    ## Detalles del Procesamiento
    - **Batch ID**: {result["batch_id"]}
    - **Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    - **Estado**: {result["status"]}
    
    ## Datos
    - **Archivo de Entrada**: {result["input_file"]}
    - **Viajes Procesados**: {result["trips_processed"]:,}
    - **Registros Guardados**: {result["records_saved"]:,}
    
    ## Información del Modelo
    - **Nombre**: {result["model_name"]}
    - **Versión**: {result["model_version"]}
    - **RMSE**: {result["model_rmse"]:.4f} minutos
    - **Origen**: Modelo local copiado del pipeline
    
    ## Estadísticas de Predicciones
    - **Duración Promedio**: {result["avg_duration"]:.2f} minutos
    - **Duración Mínima**: {result["min_duration"]:.2f} minutos
    - **Duración Máxima**: {result["max_duration"]:.2f} minutos
    - **Rango**: {result["max_duration"] - result["min_duration"]:.2f} minutos
    
    ## Almacenamiento
    - **Base de Datos**: SQL (SQLite)
    - **Ubicación**: data/database/predictions.db
    
    ## Próximos Pasos
    1. Consultar predicciones usando batch_id: `{result["batch_id"]}`
    2. Analizar distribución de predicciones
    3. Comparar con batches anteriores
    4. Monitorear performance del modelo
    """

    create_markdown_artifact(
        key="batch-prediction-summary",
        markdown=markdown_content,
        description=f"Resumen detallado del batch {result['batch_id']}",
    )

    logger.info("Artifacts de resumen creados")


@task(name="get-database-stats", description="Obtener estadísticas de la base de datos")
def get_db_stats_task():
    """
    Obtiene estadísticas de la base de datos.

    Returns:
        Dictionary con estadísticas
    """
    logger = get_run_logger()
    logger.info("Obteniendo estadísticas de la base de datos...")

    db = get_database()
    stats = db.get_statistics()

    logger.info(f"   Total Predicciones: {stats['total_predictions']:,}")
    logger.info(f"   Batches Únicos: {stats['unique_batches']}")
    logger.info(f"   Versiones de Modelo: {stats['model_versions']}")

    return stats


@flow(
    name="batch-prediction",
    description="Flow completo de predicción batch con modelo local",
)
def batch_prediction_flow(num_trips: int = None):
    """
    Flow completo de predicción batch.

    Args:
        num_trips: Número de viajes a generar (None = usar default)

    Returns:
        Dictionary con resultados del flow
    """
    logger = get_run_logger()
    logger.info("Iniciando flow de predicción batch")
    logger.info("=" * 60)

    try:
        # Paso 1: Generar datos de viajes
        logger.info("Paso 1: Generando datos de viajes de taxi")
        input_file = generate_data_task(num_trips=num_trips)

        # Paso 2: Procesar predicciones con modelo local
        logger.info("Paso 2: Procesando predicciones con modelo local")
        result = process_predictions_task(input_file)

        # Paso 3: Crear artifacts de resumen
        logger.info("Paso 3: Creando artifacts de resumen")
        create_summary_artifact(result)

        # Paso 4: Obtener estadísticas de la base de datos
        logger.info("Paso 4: Obteniendo estadísticas de la base de datos")
        db_stats = get_db_stats_task()

        # Resumen final
        logger.info("=" * 60)
        logger.info("🎉 Flow de predicción batch completado exitosamente!")
        logger.info("=" * 60)
        logger.info(f"   Batch ID: {result['batch_id']}")
        logger.info(f"   Viajes Procesados: {result['trips_processed']}")
        logger.info(f"   Modelo: {result['model_name']} v{result['model_version']}")
        logger.info(f"   Total Predicciones en DB: {db_stats['total_predictions']:,}")
        logger.info("=" * 60)

        return {
            "status": "success",
            "batch_result": result,
            "database_stats": db_stats,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error en el flow de predicción batch: {e}")
        raise


@flow(
    name="batch-prediction-scheduled",
    description="Flow programado para ejecución automática",
)
def scheduled_batch_flow():
    """
    Flow programado para ejecución automática en producción.
    """
    logger = get_run_logger()
    logger.info("Ejecutando flow programado de predicción batch")

    result = batch_prediction_flow(num_trips=None)

    return result


if __name__ == "__main__":
    # Ejecutar flow localmente para pruebas (100 viajes)
    # Para deployment automático con 1000 viajes, usar: uv run python deploy_batch.py
    
    print("Ejecutando flow de predicción batch localmente (pruebas)...")
    print("=" * 60)

    result = batch_prediction_flow(num_trips=100)

    print("\n" + "=" * 60)
    print("Ejecución del flow completada")
    print("=" * 60)
    print(f"Estado: {result['status']}")
    print(f"Batch ID: {result['batch_result']['batch_id']}")
    print(f"Viajes Procesados: {result['batch_result']['trips_processed']}")
    print(
        f"Total Predicciones en DB: {result['database_stats']['total_predictions']}"
    )
    print("=" * 60)
    print("\nPara deployment automático (1000 viajes cada hora):")
    print("  uv run python deploy_batch.py")
    print("=" * 60)
