# src/services/sensor_service.py
from typing import Dict, Any
from daos.sensor_dao import SensorDao
from services.base_service import BaseService

class SensorService(BaseService):
    def __init__(self):
        super().__init__(SensorDao())

    def create_sensor(self, sensor_id: str, model: str, resonance_frequency: float, calibration: Dict[str, Any], properties: Dict[str, Any]) -> str:
        self.dao.create(sensor_id, model, resonance_frequency, calibration, properties)
        return sensor_id

    def get_sensor(self, sensor_id: str) -> Dict[str, Any]:
        return self.dao.find_sensor_by_id(sensor_id)
