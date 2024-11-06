# rock_mechanics_lab_database/services/core_sample_service.py
from typing import Dict, Any, List
from daos.core_sample_dao import CoreSampleDao
from services.base_service import BaseService

class CoreSampleService(BaseService):
    def __init__(self):
        super().__init__(CoreSampleDao())

    def create_core_sample(self, core_sample_id: str, material: str, dimensions: Dict[str, Any]) -> str:
        self.dao.create(core_sample_id, material, dimensions)
        return core_sample_id

    def update_sensors(self, core_sample_id: str, sensors: List[Dict]) -> str:
        return self.dao.update_sensors(core_sample_id, sensors)
