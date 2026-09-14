"""
Data utility functions.
"""

import logging
from datetime import date
from typing import Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

TLC_TRIP_DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet"


def calculate_next_period(year: int, month: int) -> Tuple[int, int]:
    """
    Calculate next year and month for validation data.
    
    Args:
        year: Current year
        month: Current month
    
    Returns:
        Tuple of (next_year, next_month)
    """
    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    return next_year, next_month


def _shift_period(year: int, month: int, delta_months: int) -> Tuple[int, int]:
    """Desplaza un (year, month) hacia adelante o atrás `delta_months` meses."""
    total_months = year * 12 + (month - 1) + delta_months
    return total_months // 12, total_months % 12 + 1


def _period_exists(year: int, month: int) -> bool:
    """
    Verifica, con una petición HEAD liviana (sin descargar el parquet
    completo), si la TLC ya publicó el archivo de ese periodo.
    """
    url = TLC_TRIP_DATA_URL.format(year=year, month=month)
    try:
        response = httpx.head(url, timeout=10.0, follow_redirects=True)
        return response.status_code == 200
    except httpx.HTTPError as e:
        logger.warning(f"No se pudo verificar {year}-{month:02d} ({url}): {e}")
        return False


def find_latest_available_period(
    reference_date: Optional[date] = None,
    max_lookback_months: int = 6,
) -> Tuple[int, int]:
    """
    Encuentra el periodo (year, month) de ENTRENAMIENTO más reciente para el
    cual tanto ese mes como el siguiente (el que se usa como periodo de
    validación, ver calculate_next_period) ya están publicados por la TLC.

    La TLC publica sus datos de green taxi con un rezago que en teoría es de
    ~2 meses, pero en la práctica varía (a veces es mayor) - por eso no
    asumimos un número fijo de meses de rezago: partimos del mes actual y
    vamos retrocediendo, mes a mes, probando con una petición HEAD si el
    archivo ya existe, hasta encontrar dos meses consecutivos publicados.
    Esto es lo mismo que causaba el 403 cuando se pedía un mes que la TLC
    todavía no había publicado.

    Args:
        reference_date: fecha desde la que se calcula "el mes actual"
            (por defecto, hoy). Parámetro pensado para poder testear esta
            función con una fecha fija.
        max_lookback_months: cuántos meses hacia atrás se está dispuesta a
            retroceder antes de rendirse.

    Returns:
        Tuple (year, month) del periodo de entrenamiento.

    Raises:
        RuntimeError: si no se encuentran dos meses consecutivos publicados
            dentro de max_lookback_months.
    """
    if reference_date is None:
        reference_date = date.today()

    for lookback in range(max_lookback_months):
        val_year, val_month = _shift_period(reference_date.year, reference_date.month, -lookback)
        train_year, train_month = _shift_period(val_year, val_month, -1)

        if _period_exists(val_year, val_month) and _period_exists(train_year, train_month):
            logger.info(
                f"Periodo detectado automáticamente: entrenamiento "
                f"{train_year}-{train_month:02d}, validación "
                f"{val_year}-{val_month:02d} (retrocediendo {lookback} "
                f"mes(es) desde {reference_date.year}-{reference_date.month:02d})"
            )
            return train_year, train_month

    raise RuntimeError(
        f"No se encontraron dos meses consecutivos publicados en los "
        f"últimos {max_lookback_months} meses antes de "
        f"{reference_date.year}-{reference_date.month:02d}. Verifica "
        f"manualmente la disponibilidad en "
        f"https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"
    )
