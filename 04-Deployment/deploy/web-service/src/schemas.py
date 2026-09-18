"""
Modelos Pydantic para validación de requests y responses.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List


class TripRequest(BaseModel):
    """Request para predicción de un viaje"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "PULocationID": 161,
                "DOLocationID": 236,
                "trip_distance": 5.2
            }
        }
    )

    PULocationID: int = Field(..., description="Zona de pickup", ge=1, le=265)
    DOLocationID: int = Field(..., description="Zona de dropoff", ge=1, le=265)
    trip_distance: float = Field(..., description="Distancia del viaje en millas")

    @field_validator('trip_distance')
    @classmethod
    def validate_distance(cls, v):
        if v <= 0:
            raise ValueError('La distancia debe ser mayor a 0')
        if v > 100:
            raise ValueError('La distancia no puede ser mayor a 100 millas')
        return v


class BatchTripRequest(BaseModel):
    """Request para predicción de múltiples viajes"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trips": [
                    {"PULocationID": 161, "DOLocationID": 236, "trip_distance": 5.2},
                    {"PULocationID": 237, "DOLocationID": 238, "trip_distance": 3.8}
                ]
            }
        }
    )

    trips: List[TripRequest] = Field(..., description="Lista de viajes")

    @field_validator('trips')
    @classmethod
    def validate_trips(cls, v):
        if len(v) == 0:
            raise ValueError('Debe proporcionar al menos un viaje')
        if len(v) > 1000:
            raise ValueError('Máximo 1000 viajes por request')
        return v


class PredictionResponse(BaseModel):
    """Response de predicción individual"""
    # coerce_numbers_to_str: permite que, si algún caller llega a construir
    # esta response sin castear model_version a str manualmente, pydantic
    # lo convierta igual (verificado de forma empírica que es un config
    # real y funcional, no una opción muerta).
    model_config = ConfigDict(coerce_numbers_to_str=True)

    PULocationID: int
    DOLocationID: int
    trip_distance: float
    predicted_duration_minutes: float
    model_name: str
    model_version: str


class BatchPredictionResponse(BaseModel):
    """Response de predicción batch"""
    predictions: List[PredictionResponse]
    total: int
    model_name: str
    model_version: str


class HealthResponse(BaseModel):
    """Response del health check"""
    status: str
    model_loaded: bool
    model_name: str
    model_version: str
    model_rmse: float
