# src/api/routers/sensors.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from src.services.sensor_service import SensorService

router = APIRouter()
sensor_service = SensorService()

class SensorCreateRequest(BaseModel):
    sensor_id: str
    sensor_type: str
    resonance_frequency: float
    dimensions: Dict[str, Any]
    properties: Dict[str, Any]

@router.post("/", response_model=dict)
def create_sensor(request: SensorCreateRequest):
    try:
        print(request)  # Debugging line
        sensor_service.create_sensor(
            sensor_id=request.sensor_id,
            sensor_type=request.sensor_type,
            model=request.model,
            resonance_frequency=request.resonance_frequency,
            properties=request.properties
        )
        return {"message": "Sensor created successfully"}
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{sensor_id}", response_model=dict)
def get_sensor(sensor_id: str):
    try:
        sensor = sensor_service.get_sensor(sensor_id)
        if sensor:
            return sensor
        else:
            raise HTTPException(status_code=404, detail="Sensor not found")
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        raise HTTPException(status_code=400, detail=str(e))
