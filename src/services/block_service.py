# src/services/block_service.py
from daos.block_dao import BlockDao
from typing import Dict

class BlockService:
    def __init__(self):
        self.block_dao = BlockDao()

    def create_block(self, block_data: Dict):
        return self.block_dao.create(**block_data)

    def add_sensor_to_block(self, block_id: str, sensor_data: Dict):
        return self.block_dao.add_sensor(block_id, **sensor_data)

    def get_block_by_id(self, block_id: str):
        return self.block_dao.find_block_by_id(block_id)
