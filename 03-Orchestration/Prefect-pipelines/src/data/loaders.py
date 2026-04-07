"""
Data loading tasks with caching and retry logic.
"""

from datetime import timedelta
from pathlib import Path
from typing import Dict

import pandas as pd
from prefect import task, get_run_logger
from prefect.artifacts import create_table_artifact, create_link_artifact
from prefect.tasks import task_input_hash
from prefect.results import ResultRecord

from ..config import CATEGORICAL_FEATURES, MIN_DURATION, MAX_DURATION


@task(
    name="load_data",
    description="Download parquet file from NYC TLC",
    retries=3,
    retry_delay_seconds=[10, 30, 60],
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=24),
    persist_result=True,
    result_storage_key="train-data-{parameters[year]}-{parameters[month]:02d}.parquet"
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
    
    # Calculate duration
    df['duration'] = (df.lpep_dropoff_datetime - df.lpep_pickup_datetime).dt.total_seconds() / 60
    
    # Filter by duration
    df = df[(df.duration >= MIN_DURATION) & (df.duration <= MAX_DURATION)]
    
    # Convert categorical features
    df[CATEGORICAL_FEATURES] = df[CATEGORICAL_FEATURES].astype(str)
    
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
    
    # Save dataset as CSV artifact for training data
    data_folder = Path('data')
    data_folder.mkdir(exist_ok=True)
    
    csv_path = data_folder / f"train_data_{year}_{month:02d}.csv"
    df.to_csv(csv_path, index=False)
    
    logger.info(f"Training dataset saved to {csv_path}")
    
    # Create link artifact to the saved dataset
    create_link_artifact(
        key=f"train-dataset-{year}-{month:02d}",
        link=str(csv_path.absolute()),
        link_text=f"Training Dataset {year}-{month:02d}",
        description=f"Complete training dataset with {len(df)} records saved as CSV"
    )

    return df
