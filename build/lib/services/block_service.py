# src/services/block_service.py
from typing import Dict, List, Any
from daos.block_dao import BlockDao
from services.base_service import BaseService

class BlockService(BaseService):
    def __init__(self):
        super().__init__(BlockDao())

    def create_block(self, block_id: str, material: str, dimensions: Dict[str, float], sensor_rail_width: float, sensors: List[Dict], description: str) -> str:
        self.dao.create(block_id, material, dimensions, sensor_rail_width, sensors, description)
        return block_id

    def add_sensor(self, block_id: str, sensor_id: str, sensor_name: str, position: Dict[str, float], orientation: str, calibration: str) -> str:
        return self.dao.add_sensor(block_id, sensor_id, sensor_name, position, orientation, calibration)

    def get_block(self, block_id: str) -> Dict[str, Any]:
        return self.dao.find_block_by_id(block_id)
