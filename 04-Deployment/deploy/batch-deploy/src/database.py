"""
Database module for storing batch predictions.
Uses SQLAlchemy to store predictions in SQLite database.
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config.settings as settings

Base = declarative_base()


class Prediction(Base):
    """
    Model for storing batch predictions.
    """
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Input features
    PULocationID = Column(Integer, nullable=False)
    DOLocationID = Column(Integer, nullable=False)
    trip_distance = Column(Float, nullable=False)
    
    # Prediction output
    predicted_duration_minutes = Column(Float, nullable=False)
    
    # Model metadata
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    model_stage = Column(String(20), nullable=False)
    
    # Batch metadata
    batch_id = Column(String(50), nullable=False, index=True)
    prediction_timestamp = Column(DateTime, nullable=False, default=datetime.now)
    
    # Additional info
    run_id = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, batch={self.batch_id}, duration={self.predicted_duration_minutes:.2f})>"


class PredictionDatabase:
    """
    Database manager for batch predictions.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = settings.DB_CONNECTION_STRING
        
        self.engine = create_engine(db_path, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        print(f"📊 Database initialized: {db_path}")
    
    def save_predictions(
        self,
        df: pd.DataFrame,
        predictions: list,
        model_info: dict,
        batch_id: str = None
    ) -> int:
        """
        Save batch predictions to database.
        
        Args:
            df: DataFrame with input features
            predictions: List of predicted durations
            model_info: Dictionary with model metadata
            batch_id: Unique identifier for this batch
            
        Returns:
            Number of records saved
        """
        if batch_id is None:
            batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session = self.Session()
        
        try:
            records = []
            timestamp = datetime.now()
            
            for idx, (_, row) in enumerate(df.iterrows()):
                record = Prediction(
                    PULocationID=int(row['PULocationID']),
                    DOLocationID=int(row['DOLocationID']),
                    trip_distance=float(row['trip_distance']),
                    predicted_duration_minutes=float(predictions[idx]),
                    model_name=model_info.get('name', 'unknown'),
                    model_version=str(model_info.get('version', 'unknown')),
                    model_stage=model_info.get('stage', 'unknown'),
                    batch_id=batch_id,
                    prediction_timestamp=timestamp,
                    run_id=model_info.get('run_id')
                )
                records.append(record)
            
            # Bulk insert
            session.bulk_save_objects(records)
            session.commit()
            
            print(f"💾 Saved {len(records)} predictions to database")
            print(f"   Batch ID: {batch_id}")
            print(f"   Model: {model_info.get('name')} v{model_info.get('version')}")
            
            return len(records)
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving predictions: {e}")
            raise
        finally:
            session.close()
    
    def get_predictions_by_batch(self, batch_id: str) -> pd.DataFrame:
        """
        Retrieve predictions for a specific batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            DataFrame with predictions
        """
        session = self.Session()
        
        try:
            query = session.query(Prediction).filter(
                Prediction.batch_id == batch_id
            )
            
            results = query.all()
            
            if not results:
                print(f"⚠️  No predictions found for batch: {batch_id}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = [{
                'id': r.id,
                'PULocationID': r.PULocationID,
                'DOLocationID': r.DOLocationID,
                'trip_distance': r.trip_distance,
                'predicted_duration_minutes': r.predicted_duration_minutes,
                'model_name': r.model_name,
                'model_version': r.model_version,
                'model_stage': r.model_stage,
                'batch_id': r.batch_id,
                'prediction_timestamp': r.prediction_timestamp,
                'run_id': r.run_id
            } for r in results]
            
            df = pd.DataFrame(data)
            
            print(f"📊 Retrieved {len(df)} predictions for batch: {batch_id}")
            
            return df
            
        finally:
            session.close()
    
    def get_latest_batch(self) -> pd.DataFrame:
        """
        Get predictions from the most recent batch.
        
        Returns:
            DataFrame with latest batch predictions
        """
        session = self.Session()
        
        try:
            # Get latest batch_id
            latest = session.query(Prediction.batch_id).order_by(
                Prediction.prediction_timestamp.desc()
            ).first()
            
            if not latest:
                print("⚠️  No predictions found in database")
                return pd.DataFrame()
            
            batch_id = latest[0]
            
            return self.get_predictions_by_batch(batch_id)
            
        finally:
            session.close()
    
    def get_statistics(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        session = self.Session()
        
        try:
            total_predictions = session.query(Prediction).count()
            
            # Count unique batches
            unique_batches = session.query(Prediction.batch_id).distinct().count()
            
            # Get model versions used
            model_versions = session.query(
                Prediction.model_version
            ).distinct().all()
            
            stats = {
                'total_predictions': total_predictions,
                'unique_batches': unique_batches,
                'model_versions': [v[0] for v in model_versions]
            }
            
            return stats
            
        finally:
            session.close()
    
    def query_predictions(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        model_version: str = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Query predictions with filters.
        
        Args:
            start_date: Filter predictions after this date
            end_date: Filter predictions before this date
            model_version: Filter by model version
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with filtered predictions
        """
        session = self.Session()
        
        try:
            query = session.query(Prediction)
            
            # Apply filters
            if start_date:
                query = query.filter(Prediction.prediction_timestamp >= start_date)
            
            if end_date:
                query = query.filter(Prediction.prediction_timestamp <= end_date)
            
            if model_version:
                query = query.filter(Prediction.model_version == model_version)
            
            # Order by timestamp descending and limit
            query = query.order_by(Prediction.prediction_timestamp.desc()).limit(limit)
            
            results = query.all()
            
            if not results:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = [{
                'id': r.id,
                'PULocationID': r.PULocationID,
                'DOLocationID': r.DOLocationID,
                'trip_distance': r.trip_distance,
                'predicted_duration_minutes': r.predicted_duration_minutes,
                'model_name': r.model_name,
                'model_version': r.model_version,
                'model_stage': r.model_stage,
                'batch_id': r.batch_id,
                'prediction_timestamp': r.prediction_timestamp
            } for r in results]
            
            return pd.DataFrame(data)
            
        finally:
            session.close()


def get_database() -> PredictionDatabase:
    """
    Get database instance.
    
    Returns:
        PredictionDatabase instance
    """
    return PredictionDatabase()


if __name__ == "__main__":
    # Test database
    print("🧪 Testing database module...")
    
    db = get_database()
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"   Total Predictions: {stats['total_predictions']}")
    print(f"   Unique Batches: {stats['unique_batches']}")
    print(f"   Model Versions: {stats['model_versions']}")
    
    # Get latest batch
    if stats['total_predictions'] > 0:
        latest = db.get_latest_batch()
        print(f"\n📈 Latest Batch:")
        print(f"   Records: {len(latest)}")
        if len(latest) > 0:
            print(f"   Batch ID: {latest['batch_id'].iloc[0]}")
            print(f"   Model: {latest['model_name'].iloc[0]} v{latest['model_version'].iloc[0]}")
    
    print("\n✅ Database test completed!")
