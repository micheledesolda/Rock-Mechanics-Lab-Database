# rock_mechanics_lab_database/services/gouge_service.py
from typing import Dict, Any
from rock_mechanics_lab_database.daos.gouge_dao import GougeDao
from rock_mechanics_lab_database.services.base_service import BaseService

class GougeService(BaseService):
    def __init__(self):
        super().__init__(GougeDao())

    def create_gouge(self, gouge_id: str, material: str, grain_size_mum: str) -> str:
        self.dao.create(gouge_id, material, grain_size_mum)
        return gouge_id

    def get_gouge(self, gouge_id: str) -> Dict[str, Any]:
        return self.dao.find_gouge_by_id(gouge_id)
