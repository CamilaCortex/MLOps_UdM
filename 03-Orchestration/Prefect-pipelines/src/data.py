"""
Data loading and validation tasks.
"""

from datetime import timedelta
from typing import Tuple

import pandas as pd
from prefect import task, get_run_logger
from prefect.artifacts import create_table_artifact
from prefect.tasks import task_input_hash

from .config import MIN_RECORDS, NULL_THRESHOLD


@task(
    name="load_data",
    description="Download parquet file from NYC TLC",
    retries=3,
    retry_delay_seconds=[10, 30, 60],
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=24)
)
def read_dataframe(year: int, month: int) -> pd.DataFrame:
    """
    Load NYC taxi data from parquet file with caching and retry logic.
    
    Args:
        year: Year of the data
        month: Month of the data
    
    Returns:
        DataFrame with taxi trip data
    """
    logger = get_run_logger()
    
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'
    logger.info(f"Loading data from: {url}")
    
    df = pd.read_parquet(url)
    
    df['duration'] = (df.lpep_dropoff_datetime - df.lpep_pickup_datetime).dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    
    logger.info(f"Successfully loaded {len(df)} records")
    
    # Create data summary artifact
    summary_data = [
        ["Total Records", len(df)],
        ["Date Range", f"{year}-{month:02d}"],
        ["Avg Duration (min)", f"{df['duration'].mean():.2f}"],
        ["Median Duration (min)", f"{df['duration'].median():.2f}"]
    ]
    
    create_table_artifact(
        key=f"data-summary-{year}-{month:02d}",
        table=summary_data,
        description=f"Data summary for {year}-{month:02d}"
    )

    return df


@task(name="validate_data", description="Validate data quality before processing")
def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate data quality with basic checks.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Validated DataFrame
    """
    logger = get_run_logger()
    
    # Check for nulls
    null_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
    
    # Basic validation - solo warnings, no errores
    if len(df) < MIN_RECORDS:
        logger.warning(f"Low data volume: {len(df)} rows (recommended: {MIN_RECORDS})")
    
    if null_pct > NULL_THRESHOLD:
        logger.warning(f"High null percentage: {null_pct:.2f}%")
    
    logger.info(f"Data loaded: {len(df)} rows, {null_pct:.2f}% nulls")
    return df


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
