# rock_mechanics_lab_database/services/sensor_service.py
from typing import Dict, Any
from rock_mechanics_lab_database.daos.sensor_dao import SensorDao
from rock_mechanics_lab_database.services.base_service import BaseService

class SensorService(BaseService):
    def __init__(self):
        super().__init__(SensorDao())

    def create_sensor(self, sensor_id: str, sensor_type: str, resonance_frequency: float, dimensions: Dict[str, Any], properties: Dict[str, Any]) -> str:
        try:
            self.dao.create(sensor_id, sensor_type, resonance_frequency, dimensions, properties)
            return sensor_id
        except Exception as e:
            print(f"Error in create_sensor: {e}")  # Debugging line
            raise

    def get_sensor(self, sensor_id: str) -> Dict[str, Any]:
        try:
            return self.dao.find_sensor_by_id(sensor_id)
        except Exception as e:
            print(f"Error in get_sensor: {e}")  # Debugging line
            raise
